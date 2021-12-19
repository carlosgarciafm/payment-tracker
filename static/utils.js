// Toggle sidebar when on mobile.
const button = document.getElementById("sidebar-toggle")
const sidebar = document.getElementById("sidebar")

const left_double_arrow = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"> <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" /> </svg>'
const right_double_arrow = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"> <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" /> </svg>'

button.addEventListener("click", () => {
    let is_visible = sidebar.classList.toggle("-translate-x-full")
    if (is_visible) {
        button.innerHTML = left_double_arrow
    } else {
        button.innerHTML = right_double_arrow
    }
})
