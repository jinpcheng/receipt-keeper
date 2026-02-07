package com.receiptkeeper.api

import android.content.Context
import com.receiptkeeper.BuildConfig
import com.receiptkeeper.storage.BaseUrlStore
import com.receiptkeeper.storage.TokenStore
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
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

    private val client: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .addInterceptor(logging)
            .addInterceptor(authInterceptor)
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
}
