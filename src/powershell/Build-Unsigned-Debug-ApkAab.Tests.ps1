BeforeAll {
    . $PSCommandPath.Replace('.Tests.ps1','.ps1')
}

Describe "Build-Unsigned-Debug-ApkAab" {
    It "Should build the APK and AAB without errors using the given parameters" {
        Build-Unsigned-Debug-ApkAab -Name cactus
    }
}