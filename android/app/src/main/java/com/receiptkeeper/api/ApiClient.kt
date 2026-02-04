package com.receiptkeeper.api

import android.content.Context
import com.receiptkeeper.BuildConfig
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

    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(client)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
    }

    val authService: AuthService by lazy { retrofit.create(AuthService::class.java) }
    val receiptService: ReceiptService by lazy { retrofit.create(ReceiptService::class.java) }

    fun init(context: Context) {
        if (!initialized) {
            tokenStore = TokenStore(context.applicationContext)
            initialized = true
        }
    }
}
