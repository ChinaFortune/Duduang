"use strict";


/* =====================================================
   ELEMENTS
===================================================== */

const meaningButton =
    document.getElementById("meaningButton");

const meaningModal =
    document.getElementById("meaningModal");

const closeMeaning =
    document.getElementById("closeMeaning");

const closeMeaningBottom =
    document.getElementById("closeMeaningBottom");


/* =====================================================
   OPEN MODAL
===================================================== */

function openMeaning() {

    if (!meaningModal) {
        return;
    }


    meaningModal.classList.add("active");


    meaningModal.setAttribute(
        "aria-hidden",
        "false"
    );


    document.body.classList.add(
        "modal-open"
    );

}


/* =====================================================
   CLOSE MODAL
===================================================== */

function closeMeaningModal() {

    if (!meaningModal) {
        return;
    }


    meaningModal.classList.remove(
        "active"
    );


    meaningModal.setAttribute(
        "aria-hidden",
        "true"
    );


    document.body.classList.remove(
        "modal-open"
    );

}


/* =====================================================
   MEANING BUTTON
===================================================== */

if (meaningButton) {

    meaningButton.addEventListener(
        "click",
        openMeaning
    );

}


/* =====================================================
   CLOSE BUTTON - HEADER
===================================================== */

if (closeMeaning) {

    closeMeaning.addEventListener(
        "click",
        closeMeaningModal
    );

}


/* =====================================================
   CLOSE BUTTON - FOOTER
===================================================== */

if (closeMeaningBottom) {

    closeMeaningBottom.addEventListener(
        "click",
        closeMeaningModal
    );

}


/* =====================================================
   CLOSE WHEN CLICKING OVERLAY
===================================================== */

if (meaningModal) {

    meaningModal.addEventListener(
        "click",
        function (event) {

            if (
                event.target === meaningModal
            ) {

                closeMeaningModal();

            }

        }
    );

}


/* =====================================================
   CLOSE WITH ESCAPE
===================================================== */

document.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Escape" &&
            meaningModal &&
            meaningModal.classList.contains("active")
        ) {

            closeMeaningModal();

        }

    }
);
