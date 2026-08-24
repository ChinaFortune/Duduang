/* =========================================================
   INTRO PAGE JAVASCRIPT
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {


        /* =================================================
           BACKGROUND YIN YANG
        ================================================= */

        const yinYang =
            document.querySelector(
                ".background-yinyang"
            );


        if (!yinYang) {
            return;
        }


        /* =================================================
           MOUSE PARALLAX
           
           ทำให้หยินหยางด้านหลังขยับตามเมาส์
           พร้อมเอียงเล็กน้อยเพื่อเพิ่ม depth
        ================================================= */

        let targetX = 0;
        let targetY = 0;

        let currentX = 0;
        let currentY = 0;


        const isMobile =
            window.matchMedia(
                "(max-width: 600px)"
            ).matches;


        /*
           บนมือถือไม่ต้องทำ mouse parallax
        */

        if (!isMobile) {


            document.addEventListener(
                "mousemove",
                (event) => {

                    const centerX =
                        window.innerWidth / 2;

                    const centerY =
                        window.innerHeight / 2;


                    targetX =
                        (event.clientX - centerX)
                        / centerX;


                    targetY =
                        (event.clientY - centerY)
                        / centerY;

                },
                {
                    passive: true
                }
            );


            /* =============================================
               Smooth animation
            ============================================= */

            const animateParallax =
                () => {

                    currentX +=
                        (targetX - currentX)
                        * 0.025;


                    currentY +=
                        (targetY - currentY)
                        * 0.025;


                    /*
                       จำกัดระยะการเคลื่อนที่
                       ให้ดูเหมือนวัตถุอยู่ด้านหลัง
                    */

                    const moveX =
                        currentX * 18;


                    const moveY =
                        currentY * 18;


                    yinYang.style.setProperty(
                        "--parallax-x",
                        `${moveX}px`
                    );


                    yinYang.style.setProperty(
                        "--parallax-y",
                        `${moveY}px`
                    );


                    /*
                       เอียงตามเมาส์เล็กน้อย
                       เพื่อเพิ่มความรู้สึก depth
                    */

                    const tiltX =
                        currentY * -3.5;


                    const tiltY =
                        currentX * 3.5;


                    yinYang.style.setProperty(
                        "--tilt-x",
                        `${tiltX}deg`
                    );


                    yinYang.style.setProperty(
                        "--tilt-y",
                        `${tiltY}deg`
                    );


                    requestAnimationFrame(
                        animateParallax
                    );

                };


            animateParallax();

        }


        /* =================================================
           PAGE VISIBILITY
           
           ถ้า user เปลี่ยน tab
           หยุด animation เพื่อลดการใช้ CPU
        ================================================= */

        document.addEventListener(
            "visibilitychange",
            () => {

                if (
                    document.hidden
                ) {

                    yinYang.classList.add(
                        "is-paused"
                    );

                } else {

                    yinYang.classList.remove(
                        "is-paused"
                    );

                }

            }
        );


    }
);
