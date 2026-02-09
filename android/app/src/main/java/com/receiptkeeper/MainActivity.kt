package com.receiptkeeper

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.util.Log
import android.widget.Button
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.lifecycle.lifecycleScope
import com.receiptkeeper.api.ApiClient
import com.receiptkeeper.models.ReceiptExtractionResponse
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File

class MainActivity : AppCompatActivity() {
    private lateinit var captureButton: Button
    private lateinit var listButton: Button
    private lateinit var settingsButton: Button
    private lateinit var versionText: TextView
    private lateinit var statusText: TextView
    private lateinit var progress: ProgressBar
    private lateinit var photoUri: Uri
    private lateinit var photoFile: File

    private val takePicture = registerForActivityResult(androidx.activity.result.contract.ActivityResultContracts.TakePicture()) { success ->
        if (success) {
            uploadReceipt()
        } else {
            statusText.text = getString(R.string.capture_cancelled)
        }
    }

    private val requestCameraPermission =
        registerForActivityResult(androidx.activity.result.contract.ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) {
                launchCameraInternal()
            } else {
                statusText.text = getString(R.string.capture_permission_denied)
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        captureButton = findViewById(R.id.capture_button)
        listButton = findViewById(R.id.list_button)
        settingsButton = findViewById(R.id.settings_button)
        versionText = findViewById(R.id.main_version)
        statusText = findViewById(R.id.capture_status)
        progress = findViewById(R.id.capture_progress)

        versionText.text = getString(R.string.main_version_format, BuildConfig.VERSION_NAME, BuildConfig.VERSION_CODE)

        captureButton.setOnClickListener {
            ensureCameraPermissionAndLaunch()
        }
        listButton.setOnClickListener {
            startActivity(Intent(this, ReceiptsActivity::class.java))
        }
        settingsButton.setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }
    }

    private fun ensureCameraPermissionAndLaunch() {
        val granted = ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
        if (granted) {
            launchCameraInternal()
        } else {
            requestCameraPermission.launch(Manifest.permission.CAMERA)
        }
    }

    private fun launchCameraInternal() {
        val dir = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
        if (dir == null) {
            statusText.text = getString(R.string.capture_storage_error)
            return
        }

        try {
            // Some devices/emulators can fail to create temp files; avoid crashing the app.
            if (!dir.exists() && !dir.mkdirs()) {
                statusText.text = getString(R.string.capture_storage_error)
                return
            }
            photoFile = File.createTempFile("receipt_", ".jpg", dir)
            photoUri = FileProvider.getUriForFile(
                this,
                "${BuildConfig.APPLICATION_ID}.fileprovider",
                photoFile
            )
            takePicture.launch(photoUri)
        } catch (ex: Exception) {
            Log.e("MainActivity", "launchCamera failed", ex)
            statusText.text = getString(R.string.capture_camera_error)
        }
    }

    private fun setLoading(loading: Boolean) {
        progress.visibility = if (loading) ProgressBar.VISIBLE else ProgressBar.GONE
        captureButton.isEnabled = !loading
    }

    private fun uploadReceipt() {
        setLoading(true)
        statusText.text = getString(R.string.capture_uploading)
        val mediaType = "image/jpeg".toMediaTypeOrNull()
        val requestBody = photoFile.asRequestBody(mediaType)
        val filePart = MultipartBody.Part.createFormData("file", photoFile.name, requestBody)
        val currencyPart = "CAD".toRequestBody("text/plain".toMediaTypeOrNull())

        lifecycleScope.launch {
            try {
                val response = ApiClient.receiptService.createExtraction(filePart, currencyPart)
                statusText.text = getString(R.string.capture_uploaded)
                openReview(response)
            } catch (ex: Exception) {
                statusText.text = getString(R.string.capture_upload_failed)
            } finally {
                setLoading(false)
            }
        }
    }

    private fun openReview(response: ReceiptExtractionResponse) {
        val intent = Intent(this, ReviewActivity::class.java)
        intent.putExtra(ReviewActivity.EXTRA_EXTRACTION, response)
        startActivity(intent)
    }
}
