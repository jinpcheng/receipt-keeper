package com.receiptkeeper

import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.receiptkeeper.auth.AuthNavigator
import com.receiptkeeper.api.ApiClient
import com.receiptkeeper.models.ReceiptCreateRequest
import com.receiptkeeper.models.ReceiptExtractionResponse
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.Serializable

class ReviewActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_review)

        val extraction = getSerializableCompat(EXTRA_EXTRACTION, ReceiptExtractionResponse::class.java)
        val vendorInput = findViewById<EditText>(R.id.review_vendor)
        val totalInput = findViewById<EditText>(R.id.review_total)
        val categoryInput = findViewById<EditText>(R.id.review_category)
        val notesInput = findViewById<EditText>(R.id.review_notes)
        val statusText = findViewById<TextView>(R.id.review_status)
        val saveButton = findViewById<Button>(R.id.review_save)
        val backButton = findViewById<Button>(R.id.review_back)

        if (extraction == null) {
            statusText.text = getString(R.string.review_save_failed)
            saveButton.isEnabled = false
            return
        }

        val fields = extraction.extracted
        vendorInput.setText(fields.vendor_name ?: "")
        totalInput.setText(fields.total?.toString() ?: "")
        categoryInput.setText(fields.category ?: "")
        notesInput.setText(fields.notes ?: "")

        backButton.setOnClickListener { finish() }
        saveButton.setOnClickListener {
            saveReceipt(
                extraction,
                vendorInput.text.toString(),
                totalInput.text.toString(),
                categoryInput.text.toString(),
                notesInput.text.toString(),
                statusText
            )
        }
    }

    private fun saveReceipt(
        extraction: ReceiptExtractionResponse,
        vendor: String,
        total: String,
        category: String,
        notes: String,
        statusText: TextView
    ) {
        val fields = extraction.extracted
        val parsedTotal = total.toDoubleOrNull()
        val request = ReceiptCreateRequest(
            receipt_file_id = extraction.receipt_file_id,
            source_extraction_id = extraction.extraction_id,
            vendor_name = vendor.ifBlank { fields.vendor_name },
            location = fields.location,
            purchased_at = fields.purchased_at,
            category = category.ifBlank { fields.category },
            subtotal = fields.subtotal,
            tax = fields.tax,
            total = parsedTotal ?: fields.total,
            currency = fields.currency,
            payment_type = fields.payment_type,
            card_type = fields.card_type,
            card_last4 = fields.card_last4,
            ref_number = fields.ref_number,
            invoice_number = fields.invoice_number,
            auth_number = fields.auth_number,
            notes = notes.ifBlank { fields.notes }
        )

        lifecycleScope.launch {
            try {
                ApiClient.receiptService.createReceipt(request)
                statusText.text = getString(R.string.review_saved)
            } catch (ex: HttpException) {
                if (ex.code() == 401) {
                    AuthNavigator.goToLogin(this@ReviewActivity)
                    return@launch
                }
                statusText.text = getString(R.string.review_save_failed)
            } catch (ex: Exception) {
                statusText.text = getString(R.string.review_save_failed)
            }
        }
    }

    companion object {
        const val EXTRA_EXTRACTION = "extra_extraction"
    }

    private fun <T : Serializable> getSerializableCompat(key: String, clazz: Class<T>): T? {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getSerializableExtra(key, clazz)
        } else {
            @Suppress("DEPRECATION")
            intent.getSerializableExtra(key)?.let { value ->
                if (clazz.isInstance(value)) clazz.cast(value) else null
            }
        }
    }
}
