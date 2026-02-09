package com.receiptkeeper.api

import com.receiptkeeper.models.LoginRequest
import com.receiptkeeper.models.RefreshRequest
import com.receiptkeeper.models.RefreshResponse
import com.receiptkeeper.models.RegisterRequest
import com.receiptkeeper.models.TokenResponse
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthService {
    @POST("auth/register")
    suspend fun register(@Body payload: RegisterRequest): TokenResponse

    @POST("auth/login")
    suspend fun login(@Body payload: LoginRequest): TokenResponse

    @POST("auth/refresh")
    suspend fun refresh(@Body payload: RefreshRequest): RefreshResponse
}
