package com.receiptkeeper

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.receiptkeeper.repo.AuthRepository
import com.receiptkeeper.storage.TokenStore
import kotlinx.coroutines.launch

class AuthActivity : AppCompatActivity() {
    private val repository = AuthRepository()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_auth)

        val emailInput = findViewById<EditText>(R.id.email_input)
        val passwordInput = findViewById<EditText>(R.id.password_input)
        val loginButton = findViewById<Button>(R.id.login_button)
        val registerButton = findViewById<Button>(R.id.register_button)
        val statusText = findViewById<TextView>(R.id.status_text)
        val progress = findViewById<ProgressBar>(R.id.auth_progress)

        val tokenStore = TokenStore(this)
        if (!tokenStore.accessToken().isNullOrBlank()) {
            startActivity(Intent(this@AuthActivity, MainActivity::class.java))
            finish()
            return
        }

        fun setLoading(loading: Boolean) {
            progress.visibility = if (loading) ProgressBar.VISIBLE else ProgressBar.GONE
            loginButton.isEnabled = !loading
            registerButton.isEnabled = !loading
        }

        suspend fun handleAuth(isRegister: Boolean) {
            val email = emailInput.text.toString().trim()
            val password = passwordInput.text.toString()
            if (email.isEmpty() || password.isEmpty()) {
                statusText.text = getString(R.string.auth_error_missing_fields)
                return
            }

            setLoading(true)
            try {
                val response = if (isRegister) {
                    repository.register(email, password)
                } else {
                    repository.login(email, password)
                }
                tokenStore.save(response.access_token, response.refresh_token)
                statusText.text = getString(R.string.auth_success)
                startActivity(Intent(this@AuthActivity, MainActivity::class.java))
                finish()
            } catch (ex: Exception) {
                statusText.text = getString(R.string.auth_error_failed)
            } finally {
                setLoading(false)
            }
        }

        loginButton.setOnClickListener {
            lifecycleScope.launch {
                handleAuth(false)
            }
        }

        registerButton.setOnClickListener {
            lifecycleScope.launch {
                handleAuth(true)
            }
        }
    }
}
