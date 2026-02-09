package com.receiptkeeper.api

import android.content.Context
import com.receiptkeeper.BuildConfig
import com.receiptkeeper.storage.BaseUrlStore
import com.receiptkeeper.storage.TokenStore
import com.receiptkeeper.models.RefreshResponse
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.Authenticator
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.logging.HttpLoggingInterceptor
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory

object ApiClient {
    private var initialized = false
    private lateinit var tokenStore: TokenStore
    private lateinit var baseUrlStore: BaseUrlStore

    @Volatile
    private var retrofit: Retrofit? = null

    @Volatile
    private var retrofitBaseUrl: String? = null

    private val moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .build()

    private val logging = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BASIC
    }

    private val authInterceptor = Interceptor { chain ->
        val request = chain.request()
        val token = if (initialized) tokenStore.accessToken() else null
        val newRequest = if (!token.isNullOrBlank()) {
            request.newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        } else {
            request
        }
        chain.proceed(newRequest)
    }

    private val tokenAuthenticator = Authenticator { _, response ->
        if (!initialized) return@Authenticator null
        // Don't try to refresh if we're already calling refresh, or if we've already failed once.
        if (response.request.url.encodedPath.endsWith("/auth/refresh")) return@Authenticator null
        if (responseCount(response) >= 2) return@Authenticator null

        val refreshToken = tokenStore.refreshToken()
        if (refreshToken.isNullOrBlank()) {
            tokenStore.clear()
            return@Authenticator null
        }

        // If another request refreshed the token, just retry with the latest one.
        val currentAccess = tokenStore.accessToken()
        val requestAuth = response.request.header("Authorization")
        if (!currentAccess.isNullOrBlank() && requestAuth != null && requestAuth != "Bearer $currentAccess") {
            return@Authenticator response.request.newBuilder()
                .header("Authorization", "Bearer $currentAccess")
                .build()
        }

        val newAccess = refreshAccessToken(refreshToken) ?: run {
            tokenStore.clear()
            return@Authenticator null
        }
        tokenStore.saveAccessToken(newAccess)

        response.request.newBuilder()
            .header("Authorization", "Bearer $newAccess")
            .build()
    }

    private val client: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .addInterceptor(logging)
            .addInterceptor(authInterceptor)
            .authenticator(tokenAuthenticator)
            .build()
    }

    private fun ensureInitialized() {
        check(initialized) { "ApiClient.init(context) must be called before use." }
    }

    private fun getRetrofit(): Retrofit {
        ensureInitialized()
        val baseUrl = baseUrlStore.get()
        val current = retrofit
        if (current != null && retrofitBaseUrl == baseUrl) {
            return current
        }
        synchronized(this) {
            val again = retrofit
            if (again != null && retrofitBaseUrl == baseUrl) {
                return again
            }
            retrofitBaseUrl = baseUrl
            retrofit = Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(client)
                .addConverterFactory(MoshiConverterFactory.create(moshi))
                .build()
            return retrofit!!
        }
    }

    val authService: AuthService
        get() = getRetrofit().create(AuthService::class.java)

    val receiptService: ReceiptService
        get() = getRetrofit().create(ReceiptService::class.java)

    fun currentBaseUrl(): String = if (initialized) baseUrlStore.get() else BuildConfig.API_BASE_URL

    fun setBaseUrl(value: String) {
        ensureInitialized()
        baseUrlStore.save(value)
        synchronized(this) {
            retrofit = null
            retrofitBaseUrl = null
        }
    }

    fun init(context: Context) {
        if (!initialized) {
            tokenStore = TokenStore(context.applicationContext)
            baseUrlStore = BaseUrlStore(context.applicationContext)
            initialized = true
        }
    }

    private fun responseCount(response: okhttp3.Response): Int {
        var r: okhttp3.Response? = response
        var count = 1
        while (r?.priorResponse != null) {
            count++
            r = r.priorResponse
        }
        return count
    }

    private fun refreshAccessToken(refreshToken: String): String? {
        return try {
            val baseUrl = baseUrlStore.get()
            val url = baseUrl + "auth/refresh"

            val json = """{"refresh_token":"${refreshToken.replace("\"", "\\\"")}"}"""
            val body = json.toRequestBody("application/json".toMediaTypeOrNull())

            val request = Request.Builder()
                .url(url)
                .post(body)
                .build()

            OkHttpClient.Builder()
                .addInterceptor(logging)
                .build()
                .newCall(request)
                .execute()
                .use { resp ->
                    if (!resp.isSuccessful) return null
                    val raw = resp.body?.string() ?: return null
                    val adapter = moshi.adapter(RefreshResponse::class.java)
                    adapter.fromJson(raw)?.access_token
                }
        } catch (_: Exception) {
            null
        }
    }
}
