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
           เล็กน้อย เพื่อให้ดูมี depth
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
                       เพื่อให้ยังคงอยู่ตรงกลาง
                    */

                    const moveX =
                        currentX * 10;


                    const moveY =
                        currentY * 10;


                    yinYang.style.setProperty(
                        "--parallax-x",
                        `${moveX}px`
                    );


                    yinYang.style.setProperty(
                        "--parallax-y",
                        `${moveY}px`
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
           ลดการทำงานที่ไม่จำเป็น
        ================================================= */

        document.addEventListener(
            "visibilitychange",
            () => {

                if (
                    document.hidden
                ) {

                    yinYang.style.animationPlayState =
                        "paused";

                } else {

                    yinYang.style.animationPlayState =
                        "running";

                }

            }
        );


    }
);