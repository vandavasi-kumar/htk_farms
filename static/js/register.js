function sendEmailOTP() {

    let email = document.getElementById("email").value;

    fetch("/send-email-otp/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ email: email })
    })
        .then(async response => {

            console.log("STATUS:", response.status);   // 👈 ADD THIS

            const data = await response.json();
            console.log("DATA:", data);                // 👈 ADD THIS

            if (response.status !== 200) {
                alert(data.error);
            } else {
                alert(  data.message);
                startTimer()
            }

        })
        .catch(error => {
            console.log("FETCH ERROR:", error);
            alert("Something went wrong");
        });

}
function startTimer() {

    let time = 30;

    let timer = document.getElementById("otpTimer");

    let btn = document.getElementById("sendOtpBtn");
    console.log("Timer element:", timer); // 👈 DEBUG

    btn.disabled = true;

    let interval = setInterval(function () {

        if (time <= 0) {

            clearInterval(interval);

            timer.innerHTML = "You can resend OTP";

            btn.disabled = false;

            btn.innerText = "Resend OTP";

        }

        else {

            timer.innerHTML = "Resend OTP in " + time + " seconds";

        }

        time--;

    }, 1000);

}

function verifyOTP() {

    let otp = document.getElementById("email_otp").value;

    fetch("/verify-email-otp/", {

        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },

        body: JSON.stringify({
            otp: otp
        })

    })
        .then(response => response.json())
        .then(data => {

            let message = document.getElementById("otpMessage");

            if (data.status == "success") {

                message.innerHTML = "OTP verified successfully";
                message.style.color = "green";

            }

            else {

                message.innerHTML = "Invalid OTP";
                message.style.color = "red";

            }

        });

}