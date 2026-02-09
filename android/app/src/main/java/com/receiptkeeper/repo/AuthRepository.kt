package com.receiptkeeper.repo

import com.receiptkeeper.api.ApiClient
import com.receiptkeeper.models.LoginRequest
import com.receiptkeeper.models.RefreshRequest
import com.receiptkeeper.models.RefreshResponse
import com.receiptkeeper.models.RegisterRequest
import com.receiptkeeper.models.TokenResponse

class AuthRepository {
    suspend fun register(email: String, password: String): TokenResponse {
        return ApiClient.authService.register(RegisterRequest(email, password))
    }

    suspend fun login(email: String, password: String): TokenResponse {
        return ApiClient.authService.login(LoginRequest(email, password))
    }

    suspend fun refresh(refreshToken: String): RefreshResponse {
        return ApiClient.authService.refresh(RefreshRequest(refreshToken))
    }
}
