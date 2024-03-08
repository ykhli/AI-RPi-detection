'use client'

import { useEffect, useRef, useState } from "react";

export default function Page({ searchParams }: {
  searchParams: {
    name: string;
  }
}) {

  const videoUrl: string = `https://${process.env.NEXT_PUBLIC_BUCKET_NAME}.fly.storage.tigris.dev/${searchParams.name}`
  const [narration, setNarration] = useState("");
  const [eachNar, setEachNar] = useState("");
  const [showSpinner, setShowSpinner] = useState(false);

  useEffect(() => {
    if (narration != '') {
      let incre = 0;
      const timeoutId = setInterval(() => {
        setEachNar(narration);
        incre++;
        if (incre >= narration.length) {
          clearTimeout(timeoutId)
        }
      }, 1000)
      return () => clearTimeout(timeoutId);
    }
  }, [narration])

  const vidRef = useRef(null);
  const canRef = useRef(null);

  const handlePlayVideo = () => {
    if (vidRef.current != null) {
      vidRef.current.play();
    }
  }

  function captureFrame() {
    if (canRef.current && vidRef.current) {
      vidRef.current.pause();
      const context = canRef.current.getContext('2d');
      context.drawImage(vidRef.current, 0, 0, 640, 400);
      const dataURL = canRef.current.toDataURL('image/jpeg', 1);
      setShowSpinner(true);
      fetch(`/api/describe/`, {
        method: 'POST',
        body: JSON.stringify({
          'frame': dataURL
        })
      }).then(async (response) => {
        setShowSpinner(false);
        vidRef.current.play();
        const result = await response.text();
        setNarration(result);
      });
    }
  }

  return (
    <>
      <div className="playerContainer">
        <h3>Playing video from Tigris:</h3>
        <p>{videoUrl}</p>

        <video ref={vidRef} crossOrigin="" width="640" height="400" controls preload="auto" data-setup="{}">
          <source src={videoUrl} type="video/mp4" />
        </video>

        <div>
          <button className='button-53' onClick={handlePlayVideo} style={{ marginRight: 20 }}>
            Play
          </button>
          <button onClick={captureFrame}>
            Capture
          </button>
        </div>

        <h3>Narration using GPT 4 vision:</h3>
        <p>{eachNar}</p>

        {showSpinner && <div className="lds-ellipsis"><div></div><div></div><div></div><div></div></div>}

        <canvas ref={canRef} width="640" height="480" style={{ display: 'none' }}></canvas>
      </div>
    </>
  )
}