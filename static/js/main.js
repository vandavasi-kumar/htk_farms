function showToast(message, color = "green") {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.style.background = color;

    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}

function showLoader() {
    document.getElementById("loader").style.display = "flex";
}

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');

        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function addToCart(productId) {

    fetch(`/add-to-cart/${productId}/`)
        .then(response => response.json())
        .then(data => {

            if (data.status === "login_required") {
                var loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
                loginModal.show();
            }
            else if (data.status === "success") {
                document.getElementById("cart-count").innerText = data.cart_count;
                showToast("Added to cart ✅");
            }

        });
}

// function showToast(message, color = "green") {
//     const toast = document.getElementById("toast");
//     toast.innerText = message;
//     toast.style.background = color;
//     toast.style.display = "block";

//     setTimeout(() => {
//         toast.style.display = "none";
//     }, 3000);
// }
function updateQuantity(itemId, qty) {

    if (qty < 1) {
        alert("Minimum quantity is 1");
        return;
    }

    window.location.href = `/update-quantity/${itemId}/${qty}/`;
}

// wait until page fully loads
document.addEventListener("DOMContentLoaded", function () {

    const toggleBtn = document.getElementById("modeToggle");

    function applyMode(mode) {
        if (mode === "dark") {
            document.body.classList.add("dark-mode");
            if (toggleBtn) toggleBtn.innerHTML = "☀️ Light Mode";
        } else {
            document.body.classList.remove("dark-mode");
            if (toggleBtn) toggleBtn.innerHTML = "🌙 Dark Mode";
        }
    }

    // load saved mode (runs on EVERY page)
    let savedMode = localStorage.getItem("mode");

    if (!savedMode) {
        savedMode = window.matchMedia("(prefers-color-scheme: dark)").matches
            ? "dark"
            : "light";
    }

    applyMode(savedMode);

    // click event (safe)
    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            let currentMode = localStorage.getItem("mode") || "light";
            let newMode = currentMode === "dark" ? "light" : "dark";

            localStorage.setItem("mode", newMode);
            applyMode(newMode);
        });
    }

});


window.togglePassword = function (id) {
    let input = document.getElementById(id);
    if (!input) return;
    input.type = input.type === "password" ? "text" : "password";
}

// PASSWORD STRENGTH (SAFE)
// ============================
const passwordInput = document.getElementById("newPassword");
const strengthBar = document.getElementById("strengthBar");

if (passwordInput && strengthBar) {
    passwordInput.addEventListener("input", function () {

        const val = passwordInput.value;
        let strength = 0;

        if (val.length >= 8) strength++;
        if (/[A-Z]/.test(val)) strength++;
        if (/[0-9]/.test(val)) strength++;
        if (/[^A-Za-z0-9]/.test(val)) strength++;

        const width = strength * 25;

        strengthBar.style.width = width + "%";

        if (strength <= 1) {
            strengthBar.className = "progress-bar bg-danger";
        } else if (strength == 2) {
            strengthBar.className = "progress-bar bg-warning";
        } else {
            strengthBar.className = "progress-bar bg-success";
        }
    });
}
// 🔴 FORM VALIDATION
const form = document.querySelector("form");

if (form) {
    form.addEventListener("submit", function (e) {

        const newPass = document.getElementById("newPassword");
        const confirm = document.getElementById("confirmPassword");

        if (!newPass || !confirm) return;

        if (newPass.value.length < 8) {
            alert("Password must be at least 8 characters");
            e.preventDefault();
            return;
        }

        if (newPass.value !== confirm.value) {
            alert("Passwords do not match");
            e.preventDefault();
        }
    });
}

function sendForgotOTP() {

    let email = document.getElementById("forgot_email").value;

    fetch("/send-forgot-otp/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ email: email })
    })
        .then(async response => {

            const data = await response.json();

            if (response.status !== 200) {
                alert(data.error);
            } else {
                alert(data.message);

                startForgotTimer();   // 👈 separate timer
            }

        });
}


function startForgotTimer() {

    let time = 30;

    let timer = document.getElementById("forgotOtpTimer");
    let btn = document.getElementById("forgotOtpBtn");

    btn.disabled = true;

    let interval = setInterval(function () {

        if (time <= 0) {

            clearInterval(interval);

            timer.innerHTML = "You can resend OTP";

            btn.disabled = false;
            btn.innerText = "Resend OTP";

        } else {

            timer.innerHTML = "Resend OTP in " + time + " seconds";

        }

        time--;

    }, 1000);
} function verifyForgotOTP() {

    let otp = document.getElementById("forgot_otp").value;

    fetch("/verify-forgot-otp/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ otp: otp })
    })
        .then(response => response.json())
        .then(data => {

            let msg = document.getElementById("forgotMessage");

            if (data.status == "success") {

                msg.innerHTML = "OTP verified successfully";
                msg.style.color = "green";

                document.getElementById("forgotResetSection").style.display = "block";

            } else {

                msg.innerHTML = "Invalid OTP";
                msg.style.color = "red";

            }

        });
}

function resetForgotPassword() {

    let password = document.getElementById("forgot_password").value;
    let confirm = document.getElementById("forgot_confirm").value;

    fetch("/reset-password/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            password: password,
            confirm: confirm
        })
    })
        .then(response => response.json())
        .then(data => {

            alert(data.message || data.error);

            if (data.message) {
                location.reload();  // reload after success
            }

        });
}


function setRating(value) {
    let stars = document.querySelectorAll(".star-rating span");
    document.getElementById("ratingInput").value = value;

    stars.forEach((star, index) => {
        if (index < value) {
            star.classList.add("active");
        } else {
            star.classList.remove("active");
        }
    });
}

const contactForm = document.getElementById("contactForm");

if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
        e.preventDefault();

        let formData = new FormData(this);

        fetch("", {
            method: "POST",
            body: formData,
        })
        .then(response => response.text())
        .then(data => {
            document.body.innerHTML = data;
        });
    });
}

// payment

function showTab(type, event) {
    document.getElementById('upi-section').style.display = 'none';
    document.getElementById('card-section').style.display = 'none';
    document.getElementById('cod-section').style.display = 'none';

    document.getElementById(type + '-section').style.display = 'block';

    document.getElementById('paymentMethod').value = type.toUpperCase();

    let tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(btn => btn.classList.remove('active'));

    event.target.classList.add('active');
}

// Validation
function validatePayment() {
    let method = document.getElementById('paymentMethod').value;

    if (method === "UPI") {
        let upi = document.getElementById('upiId').value;
        let upiRegex = /^[\w.-]+@[\w.-]+$/;

        if (!upiRegex.test(upi)) {
            alert("❌ Invalid UPI ID");
            return false;
        }
    }

    if (method === "CARD") {
        let card = document.getElementById('cardNumber').value;
        let expiry = document.getElementById('expiry').value;
        let cvv = document.getElementById('cvv').value;

        let cardRegex = /^[0-9]{16}$/;
        let expiryRegex = /^(0[1-9]|1[0-2])\/\d{2}$/;
        let cvvRegex = /^[0-9]{3}$/;

        if (!cardRegex.test(card)) {
            alert("❌ Card must be 16 digits");
            return false;
        }

        if (!expiryRegex.test(expiry)) {
            alert("❌ Expiry must be MM/YY");
            return false;
        }

        if (!cvvRegex.test(cvv)) {
            alert("❌ CVV must be 3 digits");
            return false;
        }
    }

    return true;
}
