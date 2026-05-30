import React, { useRef, useState } from "react";
import { useProgress } from "@react-three/drei";
import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";
import styles from "./IntroScreen.module.scss";

const IntroScreen = () => {
  const { progress } = useProgress();
  const [shouldRender, setShouldRender] = useState(true);
  const introRef = useRef(null);

  useGSAP(() => {
    if (progress === 100) {
      const tl = gsap.timeline({
        onComplete: () => {
          setShouldRender(false);
        },
      });

      tl.to(introRef.current, {
        opacity: 0,
        duration: 1,
        ease: "power2.out",
        delay: 1.5,
      });
    }
  }, [progress]);

  if (!shouldRender) return null;

  return (
    <>
      <div ref={introRef} className={styles.introScreen}>
        <div className={styles.introScreenContent}>
          <div>
            <br /> Lorem ipsum dolor sit amet, consectetur adipiscing elit.
          </div>

          <div className={styles.progressBarContainer}>
            <div
              className={styles.progressBar}
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        <a
          href="https://www.youtube.com/watch?v=zyWD2E8AHCg"
          className="tutorial-link"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            position: "absolute",
            left: "50%",
            bottom: "25%",
            transform: "translate(-50%, -50%)",
            fontSize: "14px",
            color: "#000000ff",
            // textDecoration: "none",
          }}
        >
          Lorem ipsum dolor
        </a>
        <a
          href="https://github.com/andrewwoan/mr-pandas-psychologically-safe-portfolio"
          className="credits-link"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            position: "absolute",
            left: "50%",
            bottom: "15%",
            transform: "translate(-50%, -50%)",
            fontSize: "14px",
            color: "#000000ff",
            // textDecoration: "none",
          }}
        >
          Lorem ipsum sit amet
        </a>
      </div>
    </>
  );
};

export default IntroScreen;
