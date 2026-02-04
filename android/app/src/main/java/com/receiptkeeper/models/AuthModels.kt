package com.receiptkeeper.models

data class RegisterRequest(
    val email: String,
    val password: String
)

data class LoginRequest(
    val email: String,
    val password: String
)

data class User(
    val id: String,
    val email: String,
    val created_at: String
)

data class TokenResponse(
    val access_token: String,
    val refresh_token: String,
    val token_type: String,
    val user: User
)
