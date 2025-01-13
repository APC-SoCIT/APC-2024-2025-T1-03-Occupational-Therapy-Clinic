function toggleNav() {
    const sidenav = document.getElementById("mySidenav");
    const main = document.querySelector(".main");
    const navbar = document.querySelector(".navbar");
    const button = document.getElementById("toggleNavBtn");

    if (sidenav.style.width === "220px") {
        sidenav.style.width = "0";
        main.style.marginLeft = "0";
        navbar.style.marginLeft = "0";
    } else {
        sidenav.style.width = "220px";
        main.style.marginLeft = "220px";
        navbar.style.marginLeft = "220px";
    }
}

