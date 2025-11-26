package com.example.myapplication

sealed class AppScreen(val route: String) {
    object Main : AppScreen("main")
    object Settings : AppScreen("settings")
    
    companion object {
        fun fromRoute(route: String?): AppScreen {
            return when (route?.substringBefore("/")) {
                Main.route -> Main
                Settings.route -> Settings
                else -> Main // Default to main screen
            }
        }
    }
}