import React from "react";
import Flow from "./Flow2";
import download from "downloadjs";
import { toPng, toJpeg, toBlob, toPixelData, toSvg } from "html-to-image";

import "./styles.css";

export default function App() {
  const ref = React.useRef<HTMLDivElement>(null);

  const handleClick = React.useCallback(async () => {
    if (ref.current) {
      download(await toPng(ref.current), "occn.png");
      //download(await toSvg(ref.current), "test.svg");
    }
  }, [ref?.current]);

  return (
    <div  className="App">
      <div ref={ref} className="flow">
        <Flow />
      </div>
      <button onClick={() => handleClick()}>Download Image</button>
    </div>
  );
}
