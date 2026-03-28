
let couponAnimationPlayed = false;

// TOGGLE COUPON BOX

function toggleCoupon() {
    let box = document.getElementById("couponBox");
    box.style.display = box.style.display === "none" ? "block" : "none";
}

// APPLY COUPON (AUTO)
function applyCouponAuto(event) {

    let code = document.getElementById("couponInput").value;

    if (code.length < 3) return;

    fetch("/apply-coupon/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ coupon: code })
    })
        .then(res => res.json())
        .then(data => {

            let status = document.getElementById("couponStatus");

            // ❌ ERROR
            if (data.error) {
                status.innerText = data.error;
                status.className = "text-danger fw-bold";
                return;
            }

            // ✅ SUCCESS
            status.innerText = "Coupon Applied Successfully ✅";
            status.className = "text-success fw-bold";
            // 🎯 SHOW SAVINGS
            let savingsMsg = document.getElementById("couponSavings");
            savingsMsg.innerText = "🎉 You saved ₹" + data.discount + " using coupon!";
            if (!couponAnimationPlayed) {
                launchPetalRain(event);
                playCouponSound();
                couponAnimationPlayed = true;
            }
            // launchFlowers(event);
            // launchConfetti();

            // ✅ Update discount
            document.getElementById("discount").innerText = "₹" + data.discount;

            // ✅ Update shipping
            if (data.shipping == 0) {
                document.getElementById("shipping").innerText = "Free";
            } else {
                document.getElementById("shipping").innerText = "₹" + data.shipping;
            }

            // ✅ Update final total
            document.getElementById("finalTotal").innerText = "₹" + data.final_total;

            // ✅ Update free shipping message
            let subtotal = parseInt(document.getElementById("subtotal").innerText);
            updateFreeShipping(subtotal);
        });
}

// ============================
// FREE SHIPPING MESSAGE
// ============================
function updateFreeShipping(subtotal) {

    let msg = document.getElementById("freeShippingMsg");
    let progressBar = document.getElementById("shippingProgressBar");
    let percentText = document.getElementById("progressPercent");
    // let badge = document.getElementById("freeBadge");
    let suggestBox = document.getElementById("suggestBox");

    let target = 499;

    subtotal = Number(subtotal);

    let percent = (subtotal / target) * 100;
    if (percent > 100) percent = 100;

    progressBar.style.width = percent + "%";

    // 🎯 percentage text
    percentText.innerText = Math.floor(percent) + "% completed";

    if (subtotal < target) {
        let remaining = target - subtotal;

        msg.innerText = "Add ₹" + remaining + " more to get FREE delivery 🚚";
        msg.style.color = "#ff9800";

        progressBar.classList.remove("bg-success");
        progressBar.classList.add("bg-warning");

        // badge.style.display = "none";
        suggestBox.style.display = "block";

    } else {
        msg.innerText = "You got FREE delivery 🎉";
        msg.style.color = "#28a745";

        progressBar.classList.remove("bg-warning");
        progressBar.classList.add("bg-success");

        // badge.style.display = "inline-block";
        suggestBox.style.display = "none";
    }
}// ============================
// REMOVE COUPON
// ============================
function removeCoupon() {
    fetch("/remove-coupon/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        }
    })
        .then(res => res.json())
        .then(data => {
            location.reload();
        });
}

// ============================
// PAGE LOAD
// ============================


window.onload = function () {
    let subtotalText = document.getElementById("subtotal").innerText;

    // remove ₹ if present
    let subtotal = parseInt(subtotalText.replace("₹", "").trim());

    updateFreeShipping(subtotal);
};

// NAME
function validateName() {
    let val = document.getElementById("name").value;
    let err = document.getElementById("nameError");

    if (!/^[A-Za-z]/.test(val)) {
        err.innerText = "Name must start with alphabet";
    } else if (!/^[A-Za-z ]+$/.test(val)) {
        err.innerText = "Only letters allowed";
    } else {
        err.innerText = "";
    }
}

// PHONE
function validatePhone() {
    let val = document.getElementById("phone").value;
    let err = document.getElementById("phoneError");

    if (!/^[6-9]\d{0,9}$/.test(val)) {
        err.innerText = "Must start with 6-9";
    } else if (val.length != 10) {
        err.innerText = "Must be 10 digits";
    } else {
        err.innerText = "";
    }
}

// PINCODE
function validatePincode() {
    let val = document.getElementById("pincode").value;
    let err = document.getElementById("pincodeError");

    if (!/^\d*$/.test(val)) {
        err.innerText = "Only digits allowed";
    } else if (val.length != 6) {
        err.innerText = "Pincode must be 6 digits";
    } else {
        err.innerText = "";
    }
}

// ADDRESS 1
function validateAddress1() {
    let val = document.getElementById("address1").value;
    let err = document.getElementById("address1Error");

    if (val.length < 5) {
        err.innerText = "Enter valid address";
    } else {
        err.innerText = "";
    }
}

// ADDRESS 2
function validateAddress2() {
    let val = document.getElementById("address2").value;
    let err = document.getElementById("address2Error");

    if (val.length < 5) {
        err.innerText = "Enter valid area";
    } else {
        err.innerText = "";
    }
}




function fetchLocation() {

    let pincode = document.getElementById("pincode").value;

    if (pincode.length != 6) return;
    document.getElementById("city").value = "Loading...";
    document.getElementById("state").value = " Loading... ";

    fetch(`https://api.postalpincode.in/pincode/${pincode}`)
        .then(res => res.json())
        .then(data => {

            if (data[0].Status === "Success") {

                let postOffice = data[0].PostOffice[0];

                document.getElementById("city").value = postOffice.District;
                document.getElementById("state").value = postOffice.State;

            } else {

                document.getElementById("city").value = "";
                document.getElementById("state").value = "";
                document.getElementById("pincodeError").innerText = "Invalid Pincode";
                alert("Invalid Pincode ❌");
            }
        });
}

function removeSavedAddress() {
    fetch("/clear-address/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        }
    })
        .then(res => res.json())
        .then(data => {
            location.reload();   // 🔥 VERY IMPORTANT
        });
}

function launchFlowers(event) {

    let x = event.clientX;
    let y = event.clientY;

    for (let i = 0; i < 30; i++) {

        let petal = document.createElement("div");

        petal.innerHTML = "🌸";
        petal.style.position = "fixed";
        petal.style.left = x + "px";
        petal.style.top = y + "px";
        petal.style.fontSize = "20px";
        petal.style.pointerEvents = "none";

        document.body.appendChild(petal);

        let angle = Math.random() * 2 * Math.PI;
        let distance = Math.random() * 200 + 50;

        let moveX = Math.cos(angle) * distance;
        let moveY = Math.sin(angle) * distance;

        petal.animate([
            { transform: "translate(0,0)", opacity: 1 },
            { transform: `translate(${moveX}px, ${moveY}px) rotate(360deg)`, opacity: 0 }
        ], {
            duration: 1500,
            easing: "ease-out"
        });

        setTimeout(() => petal.remove(), 1500);
    }
}


function launchPetalRain(event) {

    // fallback center if event missing
    let baseX = event && event.clientX ? event.clientX : window.innerWidth / 2;

    for (let i = 0; i < 35; i++) {

        let petal = document.createElement("div");

        petal.innerHTML = "🌸";
        petal.style.position = "fixed";

        // ✅ spread across screen (not only left)
        let spread = 300;
        let randomX = baseX + (Math.random() * spread - spread / 2);

        petal.style.left = randomX + "px";
        petal.style.top = "-20px";

        petal.style.fontSize = "22px";
        petal.style.pointerEvents = "none";
        petal.style.zIndex = "9999";

        document.body.appendChild(petal);

        let duration = Math.random() * 2000 + 2500;

        // gentle sideways drift
        let drift = Math.random() * 200 - 100;

        petal.animate([
            { transform: "translateY(0px) rotate(0deg)", opacity: 1 },
            { transform: `translate(${drift}px, 100vh) rotate(720deg)`, opacity: 0 }
        ], {
            duration: duration,
            easing: "ease-in"
        });

        setTimeout(() => petal.remove(), duration);
    }
}
function playCouponSound() {
    let audio = new Audio("https://www.soundjay.com/buttons/sounds/button-09.mp3");
    audio.volume = 0.3;
    audio.play().catch(() => {}); // prevents console error
}