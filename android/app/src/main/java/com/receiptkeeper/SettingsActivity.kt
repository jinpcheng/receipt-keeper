package com.receiptkeeper

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.receiptkeeper.api.ApiClient
import com.receiptkeeper.storage.BaseUrlStore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request

class SettingsActivity : AppCompatActivity() {
    private val httpClient = OkHttpClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        val urlInput = findViewById<EditText>(R.id.settings_api_base_url)
        val statusText = findViewById<TextView>(R.id.settings_status)
        val progress = findViewById<ProgressBar>(R.id.settings_progress)
        val saveButton = findViewById<Button>(R.id.settings_save)
        val testButton = findViewById<Button>(R.id.settings_test)

        urlInput.setText(ApiClient.currentBaseUrl())

        fun setLoading(loading: Boolean) {
            progress.visibility = if (loading) ProgressBar.VISIBLE else ProgressBar.GONE
            saveButton.isEnabled = !loading
            testButton.isEnabled = !loading
        }

        saveButton.setOnClickListener {
            val value = urlInput.text.toString()
            val normalized = BaseUrlStore.normalize(value)
            ApiClient.setBaseUrl(normalized)
            urlInput.setText(normalized)
            statusText.text = getString(R.string.settings_saved)
        }

        testButton.setOnClickListener {
            val value = urlInput.text.toString()
            val normalized = BaseUrlStore.normalize(value)
            setLoading(true)
            statusText.text = getString(R.string.settings_testing)

            lifecycleScope.launch {
                val ok = withContext(Dispatchers.IO) {
                    try {
                        val request = Request.Builder()
                            .url(normalized + "health")
                            .get()
                            .build()
                        httpClient.newCall(request).execute().use { resp ->
                            resp.isSuccessful
                        }
                    } catch (_: Exception) {
                        false
                    }
                }
                statusText.text = if (ok) {
                    getString(R.string.settings_test_ok)
                } else {
                    getString(R.string.settings_test_failed)
                }
                setLoading(false)
            }
        }
    }
}

