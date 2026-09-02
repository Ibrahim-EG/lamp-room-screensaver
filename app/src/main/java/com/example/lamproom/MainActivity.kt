package com.example.lamproom

import android.app.Activity
import android.os.Bundle

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // We don't need a UI for the app itself, just close it immediately.
        // The user will use this via Android System Settings -> Screen Saver.
        finish() 
    }
}
