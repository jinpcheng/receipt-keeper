package com.receiptkeeper

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.TextView
import com.receiptkeeper.models.ReceiptRead

class ReceiptAdapter(
    context: Context,
    private val receipts: List<ReceiptRead>
) : ArrayAdapter<ReceiptRead>(context, R.layout.item_receipt, receipts) {
    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val view = convertView ?: LayoutInflater.from(context).inflate(R.layout.item_receipt, parent, false)
        val title = view.findViewById<TextView>(R.id.item_title)
        val subtitle = view.findViewById<TextView>(R.id.item_subtitle)

        val receipt = receipts[position]
        title.text = receipt.vendor_name ?: "Unknown vendor"
        val total = receipt.total?.toString() ?: "-"
        val date = receipt.purchased_at ?: "-"
        subtitle.text = "Total: $total  Date: $date"

        return view
    }
}
