package com.example.lamproom

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.webkit.GeolocationPermissions
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.widget.Button

class MainActivity : Activity() {
    private var webView: WebView? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val btnSettings = findViewById<Button>(R.id.btnSettings)
        val btnPreview = findViewById<Button>(R.id.btnPreview)

        btnSettings.setOnClickListener {
            try {
                startActivity(Intent(Settings.ACTION_DREAM_SETTINGS))
            } catch (e: Exception) {
                val intent = Intent(Intent.ACTION_MAIN).apply {
                    setClassName("com.android.settings", "com.android.settings.DreamSettings")
                }
                startActivity(intent)
            }
        }

        btnPreview.setOnClickListener {
            startPreview()
        }
    }

    private fun startPreview() {
        webView = WebView(this).apply {
            setLayerType(View.LAYER_TYPE_HARDWARE, null)
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.mediaPlaybackRequiresUserGesture = false
            webChromeClient = object : WebChromeClient() {
                override fun onGeolocationPermissionsShowPrompt(origin: String?, callback: GeolocationPermissions.Callback?) {
                    callback?.invoke(origin, true, false)
                }
            }
            loadUrl("file:///android_asset/index.html")
        }
        setContentView(webView)
    }

    override fun onDestroy() {
        super.onDestroy()
        webView?.destroy()
    }
}
