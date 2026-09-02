package com.example.lamproom

import android.service.dreams.DreamService
import android.webkit.GeolocationPermissions
import android.webkit.WebChromeClient
import android.webkit.WebView

class LampDreamService : DreamService() {

    private var webView: WebView? = null

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        
        isInteractive = true  // Allows tapping the screen to throw logs/pet cat
        isFullscreen = true

        webView = WebView(applicationContext).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true // Required for localStorage
            settings.mediaPlaybackRequiresUserGesture = false // Allows fire crackles
            
            webChromeClient = object : WebChromeClient() {
                override fun onGeolocationPermissionsShowPrompt(
                    origin: String?,
                    callback: GeolocationPermissions.Callback?
                ) {
                    callback?.invoke(origin, true, false) // Auto-grant GPS for Real Sky
                }
            }

            // Load your HTML file from the assets folder
            loadUrl("file:///android_asset/index.html")
        }
        
        setContentView(webView)
    }

    override fun onDreamingStarted() {
        super.onDreamingStarted()
        // Android natively keeps the screen awake and ON while this is running!
    }

    override fun onDreamingStopped() {
        super.onDreamingStopped()
        // When you unplug the phone, or press the power button, 
        // Android calls this automatically to save battery.
        webView?.stopLoading()
        webView?.destroy()
        webView = null
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        webView?.destroy()
        webView = null
    }
}
