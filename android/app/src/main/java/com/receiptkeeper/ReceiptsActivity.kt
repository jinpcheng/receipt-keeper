package com.receiptkeeper

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.ListView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.receiptkeeper.auth.AuthNavigator
import com.receiptkeeper.api.ApiClient
import com.receiptkeeper.models.ReceiptRead
import kotlinx.coroutines.launch
import retrofit2.HttpException

class ReceiptsActivity : AppCompatActivity() {
    private lateinit var listView: ListView
    private lateinit var emptyView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_receipts)

        listView = findViewById(R.id.list_view)
        emptyView = findViewById(R.id.list_empty)
        val refresh = findViewById<Button>(R.id.list_refresh)

        refresh.setOnClickListener { loadReceipts() }
        listView.setOnItemClickListener { _, _, position, _ ->
            val receipt = listView.adapter.getItem(position) as ReceiptRead
            val intent = Intent(this, ReceiptDetailActivity::class.java)
            intent.putExtra(ReceiptDetailActivity.EXTRA_RECEIPT, receipt)
            startActivity(intent)
        }

        loadReceipts()
    }

    private fun loadReceipts() {
        lifecycleScope.launch {
            try {
                val response = ApiClient.receiptService.listReceipts(page = 1, pageSize = 50)
                val items = response.items
                if (items.isEmpty()) {
                    emptyView.visibility = TextView.VISIBLE
                } else {
                    emptyView.visibility = TextView.GONE
                }
                listView.adapter = ReceiptAdapter(this@ReceiptsActivity, items)
            } catch (ex: HttpException) {
                if (ex.code() == 401) {
                    AuthNavigator.goToLogin(this@ReceiptsActivity)
                    return@launch
                }
                emptyView.text = getString(R.string.list_empty)
                emptyView.visibility = TextView.VISIBLE
            } catch (ex: Exception) {
                emptyView.text = getString(R.string.list_empty)
                emptyView.visibility = TextView.VISIBLE
            }
        }
    }
}
