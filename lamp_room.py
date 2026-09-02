#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAMP ROOM 4.1 — real sky screensaver + detailed fireplace.
Pure Python stdlib. Auto-creates a self-signed TLS cert (needs openssl).

Usage:  python lamp_room.py [port]
"""

import os
import shutil
import socket
import ssl
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(BASE_DIR, "key.pem")
CRT_FILE = os.path.join(BASE_DIR, "cert.pem")

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">
<meta name="theme-color" content="#050507">
<link rel="icon" href="data:,">
<title>Lamp Room — screensaver</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
html,body{height:100%}
body{
  font-family:"Segoe UI",system-ui,-apple-system,Roboto,sans-serif;
  background:
    radial-gradient(140% 100% at 50% 115%, #0a0a10 0%, transparent 55%),
    linear-gradient(180deg,#020204 0%,#050508 55%,#0a0a0f 100%);
  color:#cfcfd6;overflow:hidden;user-select:none;touch-action:manipulation;
  --on:0; --lum:1; --sway:0deg; --lampH:36vh;
}
body.lamp-on{--on:1}
body.idle,body.idle *{cursor:none!important}
.scene{position:fixed;inset:0;overflow:hidden;isolation:isolate}

.layer-far,.layer-mid{position:absolute;inset:0;pointer-events:none}

.scene-stars{position:absolute;inset:0;pointer-events:none;
  opacity:calc(.38 - var(--on)*.26);transition:opacity 1s ease;
  background-image:
    radial-gradient(1px 1px at 8% 14%,rgba(255,255,255,.55),transparent),
    radial-gradient(1px 1px at 22% 6%,rgba(255,255,255,.4),transparent),
    radial-gradient(1.4px 1.4px at 37% 16%,rgba(255,255,255,.35),transparent),
    radial-gradient(1px 1px at 49% 4%,rgba(255,255,255,.45),transparent),
    radial-gradient(1px 1px at 58% 20%,rgba(255,255,255,.3),transparent),
    radial-gradient(1.4px 1.4px at 67% 9%,rgba(255,255,255,.4),transparent),
    radial-gradient(1px 1px at 76% 26%,rgba(255,255,255,.3),transparent),
    radial-gradient(1px 1px at 84% 5%,rgba(255,255,255,.45),transparent),
    radial-gradient(1px 1px at 92% 18%,rgba(255,255,255,.35),transparent),
    radial-gradient(1px 1px at 15% 30%,rgba(255,255,255,.22),transparent);
}

#windowEl,#frame1,#frame2,#clockEl,#plantEl,#catEl,#fireplaceEl{
  transition:filter .5s linear;
  filter:brightness(1) drop-shadow(0px 0px 2px rgba(255,208,150,0))
         drop-shadow(0px 0px 9px rgba(255,192,122,0))
         drop-shadow(0px 0px 24px rgba(255,180,110,0));
}
#timeplate{
  transition:filter .5s linear;
  filter:brightness(.55) drop-shadow(0px 0px 2px rgba(255,208,150,0))
         drop-shadow(0px 0px 9px rgba(255,192,122,0))
         drop-shadow(0px 0px 24px rgba(255,180,110,0));
}

/* ============================================================
   WINDOW
   ============================================================ */
.window{position:absolute;left:4vw;top:8vh;width:max(160px,14vw);height:30vh;
  border:5px solid #101014;border-radius:6px;background:#070b18;
  box-shadow:inset 0 0 24px rgba(0,0,0,.8),0 0 0 1px rgba(255,255,255,.04);
  overflow:hidden;pointer-events:auto;cursor:pointer;
}
.window .bars-v,.window .bars-h{position:absolute;background:#101014;z-index:4}
.bars-v{left:50%;top:0;bottom:0;width:4px;transform:translateX(-50%)}
.bars-h{top:50%;left:0;right:0;height:4px;transform:translateY(-50%)}
.sky{position:absolute;inset:0;transition:opacity 4s ease}
.nightbits{position:absolute;inset:0;transition:opacity 1.5s ease}
.win-stars{position:absolute;inset:0;
  background-image:
    radial-gradient(1px 1px at 18% 22%,#cfd8ff,transparent),
    radial-gradient(1px 1px at 64% 12%,#ffffff,transparent),
    radial-gradient(1px 1px at 82% 34%,#aab6ff,transparent),
    radial-gradient(1px 1px at 30% 48%,#ffffff,transparent),
    radial-gradient(1px 1px at 52% 30%,#cfd8ff,transparent),
    radial-gradient(1px 1px at 12% 64%,#ffffff,transparent),
    radial-gradient(1px 1px at 74% 58%,#cfd8ff,transparent),
    radial-gradient(1.3px 1.3px at 42% 16%,#ffffff,transparent);
  animation:twinkleB 4s ease-in-out infinite alternate;
}
@keyframes twinkleB{from{opacity:.6}to{opacity:1}}
.sun{position:absolute;width:42px;height:42px;border-radius:50%;z-index:2;opacity:0;
  background:radial-gradient(circle at 42% 38%,#fff8e0,#ffd98a 55%,#ffb054 90%);
  box-shadow:0 0 22px 8px rgba(255,205,120,.55),0 0 80px 30px rgba(255,170,80,.25);
  transition:left 35s linear,top 35s linear,opacity 2s ease,transform 35s linear}
.moon{position:absolute;width:46px;height:46px;border-radius:50%;z-index:2;opacity:0;overflow:hidden;
  background:
    radial-gradient(circle at 30% 30%, rgba(170,185,225,.45) 0 7%, transparent 8%),
    radial-gradient(circle at 63% 56%, rgba(160,175,220,.4) 0 10%, transparent 11%),
    radial-gradient(circle at 47% 74%, rgba(170,185,225,.32) 0 5%, transparent 6%),
    radial-gradient(circle at 74% 28%, rgba(165,180,222,.3) 0 4%, transparent 5%),
    radial-gradient(circle at 22% 58%, rgba(175,190,228,.26) 0 6%, transparent 7%),
    radial-gradient(circle at 40% 44%, rgba(205,215,245,.28) 0 16%, transparent 17%),
    radial-gradient(circle at 50% 50%, transparent 58%, rgba(150,165,215,.3) 96%),
    radial-gradient(circle at 42% 38%, #ffffff, #dfe6ff 55%, #b9c4f0 90%);
  box-shadow:0 0 18px 6px rgba(200,215,255,.5),0 0 70px 26px rgba(160,185,255,.22);
  transition:left 35s linear,top 35s linear,opacity 2s ease}
.cloud{position:absolute;height:14px;border-radius:20px;filter:blur(4px);z-index:3;
  background:var(--cloudCol,rgba(9,13,30,.9));animation:cloudDrift linear infinite;
}
.cloud.c1{width:70px;top:26%;animation-duration:44s;animation-delay:-12s}
.cloud.c2{width:95px;top:58%;animation-duration:62s;animation-delay:-30s;opacity:.85}
.cloud.c3{width:56px;top:74%;animation-duration:52s;animation-delay:-4s;opacity:.65}
@keyframes cloudDrift{from{transform:translateX(-120%)}to{transform:translateX(320%)}}
.shoot{position:absolute;top:16%;left:72%;width:46px;height:1.5px;border-radius:2px;z-index:3;
  background:linear-gradient(90deg,rgba(255,255,255,0),#fff);
  opacity:0;animation:shoot 13s linear infinite;
}
.shoot.s2{top:38%;left:86%;width:32px;animation-delay:6.5s;animation-duration:17s}
@keyframes shoot{
  0%{opacity:0;transform:rotate(160deg) translateX(0)}
  1%{opacity:.9}
  4%{opacity:0;transform:rotate(160deg) translateX(90px)}
  100%{opacity:0;transform:rotate(160deg) translateX(90px)}
}
.win-sheen{position:absolute;inset:0;z-index:5;pointer-events:none;
  background:linear-gradient(115deg,transparent 30%,rgba(255,255,255,.045) 46%,transparent 60%)}
.curtain{position:absolute;top:-2px;bottom:-2px;width:56%;z-index:6;
  background:
    linear-gradient(180deg,rgba(255,255,255,.05),transparent 12%,transparent 82%,rgba(0,0,0,.4)),
    repeating-linear-gradient(90deg,#2a1518 0 7px,#3d2024 7px 15px,#241114 15px 22px);
  box-shadow:inset 0 -14px 20px rgba(0,0,0,.55),0 0 14px rgba(0,0,0,.6);
  transition:transform 2.3s cubic-bezier(.65,0,.35,1);
}
.curtain.cl{left:0;transform:translateX(-94%)}
.curtain.cr{right:0;transform:translateX(94%)}
.window.closed .curtain.cl{transform:translateX(-4%)}
.window.closed .curtain.cr{transform:translateX(4%)}

.moonshaft{position:absolute;left:4vw;top:9vh;width:52vw;height:79vh;pointer-events:none;
  clip-path:polygon(0 0,26.9% 0,74% 100%,22% 100%);
  filter:blur(3px);mix-blend-mode:screen;opacity:0;transition:opacity .5s ease;
}
.daylight{position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;opacity:0;
  transition:opacity .8s ease;
  background:linear-gradient(100deg,rgba(255,216,164,.5),rgba(255,216,164,0) 60%)}
.daypool{position:absolute;left:26vw;bottom:3.5vh;width:46vw;height:11vh;border-radius:50%;
  background:radial-gradient(closest-side,rgba(255,214,150,.30),rgba(255,205,130,.10) 55%,transparent 76%);
  filter:blur(5px);mix-blend-mode:screen;opacity:0;pointer-events:none;transition:opacity .8s ease}

/* ============================================================
   PAINTINGS + WALL CLOCK
   ============================================================ */
.frame{position:absolute;border:3px solid transparent;border-radius:2px;
  background:
    linear-gradient(#0d0d12,#0d0d12) padding-box,
    linear-gradient(160deg,#8a744a,#4a3d24 35%,#b39a63 55%,#5c4c2e 80%,#3a2f1c) border-box;
  box-shadow:0 8px 22px rgba(0,0,0,.55),inset 0 0 0 1px rgba(0,0,0,.5);
}
.frame .art{position:absolute;inset:3px;overflow:hidden;border-radius:1px;
  box-shadow:inset 0 0 0 1px rgba(0,0,0,.65),inset 0 0 8px rgba(0,0,0,.5)}
.frame .glass{position:absolute;inset:0;z-index:3;pointer-events:none;
  background:linear-gradient(115deg,transparent 32%,rgba(255,255,255,.07) 46%,rgba(255,255,255,.02) 52%,transparent 62%)}
.frame.f1{left:42vw;top:11vh;width:10vmin;height:13vmin}
.frame.f2{left:53vw;top:16vh;width:8vmin;height:10vmin}
.f1 .artsky{position:absolute;inset:0;
  background:linear-gradient(180deg,#1d1626 0%,#3b2338 34%,#7a3b30 62%,#c96f3a 78%,#e8a45c 87%,#3a2016 88%,#241510 100%)}
.f1 .sunp{position:absolute;left:27%;top:52%;width:15%;aspect-ratio:1;border-radius:50%;
  background:radial-gradient(circle,#ffe3ae,#f2a45c 68%,rgba(242,164,92,0));
  box-shadow:0 0 10px 3px rgba(255,190,110,.55)}
.f1 .mtn{position:absolute;bottom:12%;width:72%;height:48%;
  clip-path:polygon(0 100%,50% 0,100% 100%)}
.f1 .m1{left:-14%;background:#241523}
.f1 .m2{right:-18%;height:38%;background:#180f1a}
.f2 .seasky{position:absolute;inset:0;
  background:linear-gradient(180deg,#0a1226 0%,#101b38 44%,#1c2c56 61%,#0b1226 62%,#070d1c 100%)}
.f2 .moon2{position:absolute;right:22%;top:20%;width:17%;aspect-ratio:1;border-radius:50%;
  background:radial-gradient(circle at 40% 35%,#f4f6ff,#c9d4f5);
  box-shadow:0 0 9px 2px rgba(190,205,255,.55)}
.f2 .ref{position:absolute;left:67%;top:62%;width:6%;height:30%;filter:blur(1px);
  background:linear-gradient(180deg,rgba(200,215,255,.5),rgba(200,215,255,0))}
.f2 .wave{position:absolute;left:8%;right:10%;height:1px;background:rgba(255,255,255,.06)}
.f2 .w1{top:70%}.f2 .w2{top:80%;left:16%;right:18%;background:rgba(255,255,255,.045)}

.clockw{position:absolute;left:61vw;top:12vh;width:8vmin;height:15vmin;min-width:56px}
.clock-face{position:relative;width:8vmin;min-width:56px;aspect-ratio:1;border-radius:50%;
  background:
    radial-gradient(circle at 50% 50%,#15151b 0 62%,transparent 63%),
    repeating-conic-gradient(rgba(255,235,200,.35) 0deg .9deg,transparent .9deg 30deg),
    radial-gradient(circle,#0d0d12,#0a0a0e);
  border:3px solid #17171d;box-shadow:0 6px 16px rgba(0,0,0,.6),inset 0 0 10px rgba(0,0,0,.7)}
.hand{position:absolute;left:50%;bottom:50%;transform-origin:50% 100%;border-radius:3px;
  background:linear-gradient(180deg,#e8d9b8,#9a8a68)}
.hand.h{width:3px;height:24%;margin-left:-1.5px}
.hand.m{width:2px;height:35%;margin-left:-1px}
.hand.s{width:1px;height:40%;margin-left:-.5px;background:linear-gradient(180deg,#ffb64d,#a86f2a)}
.clock-pin{position:absolute;left:50%;top:50%;width:6px;height:6px;margin:-3px 0 0 -3px;border-radius:50%;
  background:radial-gradient(circle at 35% 30%,#ffe9c0,#8a7a58)}
.clock-case{position:absolute;left:50%;top:calc(8vmin + 2px);transform:translateX(-50%);
  width:5vmin;min-width:34px;height:7vmin;border:3px solid #17171d;border-radius:4px;
  background:linear-gradient(180deg,#101015,#0b0b0f);overflow:hidden}
.pendulum{position:absolute;left:50%;top:2px;width:2px;height:78%;margin-left:-1px;
  background:linear-gradient(180deg,#b09a6a,#6a5a3a);transform-origin:top center;
  animation:pendSwing 1.1s ease-in-out infinite alternate}
.pendulum::after{content:"";position:absolute;bottom:-6px;left:50%;transform:translateX(-50%);
  width:10px;height:10px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ffe9c0,#8a7a58)}
@keyframes pendSwing{from{transform:rotate(-13deg)}to{transform:rotate(13deg)}}

/* ============================================================
   FLOOR / RUG / POOLS
   ============================================================ */
.floor{position:absolute;left:-4%;right:-4%;bottom:0;height:16vh;overflow:hidden;
  background:
    repeating-linear-gradient(90deg,rgba(255,255,255,.022) 0 1px,transparent 1px 92px),
    repeating-linear-gradient(0deg,rgba(0,0,0,.28) 0 1px,transparent 1px 24px),
    linear-gradient(180deg,#0b0b0f 0%,#070709 100%);
  box-shadow:inset 0 14px 24px -14px rgba(0,0,0,.9)}
.floor-sheen{position:absolute;inset:-20% -30%;pointer-events:none;opacity:var(--on);
  transition:opacity .6s ease;will-change:transform;
  background:radial-gradient(38% 90% at 27% 0%,rgba(255,205,140,.10),transparent 70%)}
.baseboard{position:absolute;left:0;right:0;bottom:16vh;height:7px;
  background:linear-gradient(180deg,#101014,#0a0a0d);
  border-top:1px solid rgba(255,255,255,.03);transition:border-color .8s}
body.lamp-on .baseboard{border-top-color:rgba(255,205,150,.12)}
.rug{position:absolute;left:24%;bottom:6.5vh;width:56vmin;height:12vmin;transform:translateX(-50%);
  border-radius:50%;
  background:
    radial-gradient(closest-side,rgba(120,60,40,.16),rgba(120,60,40,.07) 62%,transparent 72%),
    radial-gradient(closest-side,#0d0b0e,#0a090c 70%,transparent 72%);
  border:1px solid rgba(255,255,255,.028)}
.rug::after{content:"";position:absolute;inset:12%;border-radius:50%;border:1px dashed rgba(255,220,180,.06)}
.rug-light,.floorpool{position:absolute;left:0;transform:translateX(-50%);pointer-events:none;
  mix-blend-mode:screen;opacity:0;border-radius:50%;will-change:transform,opacity;
  transition:opacity .3s ease}
.rug-light{bottom:6vh;width:58vmin;height:11vmin;filter:blur(4px);
  background:radial-gradient(closest-side,rgba(255,210,146,.28),rgba(255,200,120,.09) 58%,transparent 76%)}
.floorpool{bottom:4.5vh;width:74vmin;height:16vmin;filter:blur(6px);
  background:radial-gradient(closest-side,rgba(255,210,144,.32),rgba(255,200,120,.10) 55%,transparent 75%)}

/* ============================================================
   PLANT
   ============================================================ */
.plant{position:absolute;left:20.5vw;bottom:15vh;width:14vmin;height:17vmin}
.plant-pot{position:absolute;bottom:0;left:50%;transform:translateX(-50%);
  width:50%;height:22%;clip-path:polygon(6% 0,94% 0,80% 100%,20% 100%);
  background:linear-gradient(90deg,#22120a,#3d2013 30%,#4a2817 52%,#33190e 78%,#1c0e07)}
.plant-rim{position:absolute;bottom:20%;left:50%;transform:translateX(-50%);
  width:57%;height:6.5%;border-radius:2px;
  background:linear-gradient(90deg,#2a1609,#4a2817 45%,#5c3320 55%,#241207);
  box-shadow:0 2px 3px rgba(0,0,0,.5)}
.plant-soil{position:absolute;bottom:25%;left:50%;transform:translateX(-50%);
  width:42%;height:3.5%;border-radius:50%;background:#140c07}
.plant-leaves{position:absolute;bottom:25%;left:50%;width:100%;height:75%;transform:translateX(-50%)}
.plant-leaves i{position:absolute;bottom:0;left:50%;width:11%;border-radius:50% 50% 0 0;
  background:linear-gradient(90deg,#0a130d 0%,#14251a 46%,#1c3324 50%,#14251a 54%,#0a130d 100%);
  transform-origin:bottom center}
.plant-leaves i:nth-child(1){transform:rotate(-58deg);height:62%}
.plant-leaves i:nth-child(2){transform:rotate(-38deg);height:82%}
.plant-leaves i:nth-child(3){transform:rotate(-22deg);height:94%;width:12%}
.plant-leaves i:nth-child(4){transform:rotate(-8deg);height:100%}
.plant-leaves i:nth-child(5){transform:rotate(5deg);height:97%;width:12%}
.plant-leaves i:nth-child(6){transform:rotate(20deg);height:88%}
.plant-leaves i:nth-child(7){transform:rotate(38deg);height:76%}
.plant-leaves i:nth-child(8){transform:rotate(58deg);height:58%}

/* ============================================================
   FIREPLACE — tap body = door, tap log pile = feed the fire
   ============================================================ */
.fireplace{position:absolute;left:4.5vw;bottom:16vh;width:13vw;min-width:150px;height:24vh;pointer-events:auto}
.fp-mantle{position:absolute;top:0;left:-4%;width:108%;height:9%;z-index:2;
  background:linear-gradient(180deg,#2b1c12,#1a100a);border-radius:2px;
  box-shadow:0 3px 8px rgba(0,0,0,.6)}
.fp-book{position:absolute;top:-14px;width:5px;border-radius:1px 1px 0 0}
.fp-book.b1{left:10%;height:14px;background:#26202e}
.fp-book.b2{left:15%;height:17px;background:#1e242c}
.fp-book.b3{left:20.5%;height:12px;background:#2a2018;transform:rotate(9deg);transform-origin:bottom left}
.fp-candle{position:absolute;top:-13px;right:12%;width:6px;height:13px;border-radius:2px;
  background:linear-gradient(90deg,#8f8158,#cbb98a 45%,#a0906a)}
.fp-candle::after{content:"";position:absolute;top:-6px;left:50%;transform:translateX(-50%);
  width:4px;height:6px;border-radius:50% 50% 45% 45%;
  background:radial-gradient(circle at 50% 70%,#fff3c0,#ffb64d 60%,rgba(255,150,50,0));
  animation:candleF 1.4s ease-in-out infinite alternate}
@keyframes candleF{from{transform:translateX(-50%) scaleY(1) skewX(-4deg)}to{transform:translateX(-50%) scaleY(1.25) skewX(5deg)}}
.fp-body{position:absolute;top:9%;left:0;right:0;bottom:10%;cursor:pointer;
  background:
    linear-gradient(180deg,rgba(255,255,255,.03),transparent 20%),
    repeating-linear-gradient(0deg,#1c1416 0 9px,#141012 9px 11px),
    repeating-linear-gradient(90deg,rgba(0,0,0,.25) 0 1px,transparent 1px 22px),
    #1a1315;
  box-shadow:inset 0 0 14px rgba(0,0,0,.7),0 6px 14px rgba(0,0,0,.5);
  border-radius:3px;
}
.fp-mouth{position:absolute;left:14%;right:14%;top:16%;bottom:0;
  background:radial-gradient(120% 100% at 50% 100%,#1a0f08 0%,#0a0605 55%,#040303 100%);
  border-radius:46% 46% 0 0/34% 34% 0 0;
  box-shadow:inset 0 0 18px rgba(0,0,0,.9);
  overflow:hidden;
}
.fp-glow{position:absolute;left:0;right:0;bottom:0;height:72%;pointer-events:none;z-index:4;
  background:radial-gradient(90% 90% at 50% 100%,rgba(255,150,50,.5),rgba(255,110,30,.18) 55%,transparent 80%);
  opacity:.8;mix-blend-mode:screen}
.fp-hearth{position:absolute;bottom:-6%;left:-8%;width:116%;height:10%;
  background:linear-gradient(180deg,#232022,#131113);border-radius:2px;
  box-shadow:0 4px 10px rgba(0,0,0,.55)}
/* logs — separate from the flames, they never inflate */
.logs{position:absolute;left:50%;bottom:4%;width:72%;height:26%;transform:translateX(-50%);z-index:1}
.logs i{position:absolute;width:88%;height:34%;border-radius:6px;
  background:
    repeating-linear-gradient(90deg,rgba(0,0,0,.28) 0 7px,transparent 7px 15px),
    linear-gradient(180deg,#2c180e,#180c06 70%,#120803);
  box-shadow:inset 0 -3px 6px rgba(255,110,25,.30),0 2px 4px rgba(0,0,0,.6)}
.logs i::before{content:"";position:absolute;right:1px;top:12%;width:9%;height:76%;border-radius:50%;
  background:radial-gradient(circle at 45% 45%,#6a4a2e,#3a2617 70%)}
.logs i::after{content:"";position:absolute;left:8%;right:12%;top:52%;height:2px;border-radius:2px;
  background:linear-gradient(90deg,transparent,rgba(255,140,40,.55) 30%,rgba(255,190,80,.75) 50%,rgba(255,140,40,.55) 70%,transparent);
  animation:seamGlow 1.6s ease-in-out infinite alternate;filter:blur(.5px)}
@keyframes seamGlow{from{opacity:.3}to{opacity:.95}}
.logs i:nth-child(1){left:2%;bottom:0;transform:rotate(-7deg)}
.logs i:nth-child(2){left:10%;bottom:30%;transform:rotate(6deg)}
.logs i:nth-child(3){display:none;left:6%;bottom:60%;transform:rotate(-3deg)}
.logs i:nth-child(4){display:none;left:14%;bottom:88%;transform:rotate(3deg)}
.logs.l3 i:nth-child(3){display:block}
.logs.l4 i:nth-child(3){display:block}
.logs.l4 i:nth-child(4){display:block}
/* the flames */
.fire{position:absolute;left:0;right:0;bottom:0;height:78%;pointer-events:none;
  transform-origin:50% 100%;z-index:2;transition:opacity .5s ease}
.fireplace.door-closed .fire{opacity:.82}
.fire .fl{position:absolute;bottom:6%;transform-origin:50% 100%;mix-blend-mode:screen;
  border-radius:48% 52% 30% 34%/72% 68% 22% 26%}
.fl.f0{left:14%;width:72%;height:40%;filter:blur(9px);
  background:radial-gradient(60% 80% at 50% 90%,rgba(255,80,10,.8),rgba(255,60,10,.3) 60%,transparent 82%);
  animation:danceA 1.3s ease-in-out infinite alternate}
.fl.f1{left:20%;width:26%;height:72%;filter:blur(7px);
  background:radial-gradient(50% 62% at 50% 86%,rgba(255,120,25,.9),rgba(255,80,15,.35) 60%,transparent 82%);
  animation:danceB 1.05s ease-in-out infinite alternate}
.fl.f2{left:34%;width:20%;height:92%;filter:blur(6px);
  background:radial-gradient(50% 62% at 50% 86%,rgba(255,165,45,.95),rgba(255,120,25,.4) 60%,transparent 84%);
  animation:danceA .82s ease-in-out .12s infinite alternate}
.fl.f3{left:46%;width:16%;height:64%;filter:blur(6px);
  background:radial-gradient(50% 60% at 50% 84%,rgba(255,210,90,.95),rgba(255,170,50,.45) 62%,transparent 85%);
  animation:danceC .68s ease-in-out infinite alternate}
.fl.f4{left:56%;width:18%;height:84%;filter:blur(6px);
  background:radial-gradient(50% 62% at 50% 86%,rgba(255,180,55,.95),rgba(255,130,30,.42) 60%,transparent 84%);
  animation:danceB .74s ease-in-out .2s infinite alternate}
.fl.f5{left:70%;width:14%;height:56%;filter:blur(5px);
  background:radial-gradient(50% 60% at 50% 84%,rgba(255,190,70,.9),rgba(255,140,35,.4) 62%,transparent 85%);
  animation:danceA .6s ease-in-out .08s infinite alternate}
.fl.fc{left:43%;width:13%;height:46%;filter:blur(3px);
  background:radial-gradient(50% 62% at 50% 82%,rgba(255,248,214,1),rgba(255,230,140,.55) 60%,transparent 86%);
  animation:danceB .48s ease-in-out infinite alternate}
@keyframes danceA{from{transform:scaleY(.86) skewX(-3deg)}to{transform:scaleY(1.14) skewX(3deg) translateY(-5%)}}
@keyframes danceB{from{transform:scaleY(1.1) skewX(2.5deg)}to{transform:scaleY(.84) skewX(-2.5deg) translateY(2%)}}
@keyframes danceC{from{transform:scaleY(.9) skewX(-2deg) translateX(-3%)}to{transform:scaleY(1.18) skewX(2deg) translateX(3%) translateY(-7%)}}
.fire.surge{animation:surgeUp 1.1s ease-out}
@keyframes surgeUp{0%{transform:scaleY(1)}18%{transform:scaleY(1.26)}55%{transform:scaleY(1.06)}100%{transform:scaleY(1)}}
/* glowing coals */
.coals{position:absolute;left:50%;bottom:-2%;width:82%;height:16%;transform:translateX(-50%)}
.coals b{position:absolute;bottom:0;border-radius:42% 48% 50% 45%;
  background:radial-gradient(circle at 50% 38%,#ffb35a 0%,#e0501a 42%,#7a1f08 78%,#3a0f05 100%);
  box-shadow:0 0 8px 2px rgba(255,120,30,.45);
  animation:coalPulse ease-in-out infinite alternate}
.coals b:nth-child(1){left:3%;width:16%;height:60%;animation-duration:1.1s}
.coals b:nth-child(2){left:18%;width:13%;height:46%;animation-duration:1.45s;animation-delay:.2s}
.coals b:nth-child(3){left:31%;width:17%;height:66%;animation-duration:.9s;animation-delay:.1s}
.coals b:nth-child(4){left:47%;width:12%;height:50%;animation-duration:1.25s;animation-delay:.35s}
.coals b:nth-child(5){left:58%;width:16%;height:62%;animation-duration:1.05s}
.coals b:nth-child(6){left:73%;width:12%;height:44%;animation-duration:1.5s;animation-delay:.25s}
.coals b:nth-child(7){left:85%;width:12%;height:54%;animation-duration:.95s;animation-delay:.4s}
@keyframes coalPulse{from{filter:brightness(.7)}to{filter:brightness(1.35)}}
/* smoke wisps */
.smoke{position:absolute;inset:0;pointer-events:none}
.smoke i{position:absolute;bottom:58%;width:22px;height:22px;border-radius:50%;
  background:radial-gradient(circle,rgba(150,150,160,.20),rgba(150,150,160,0) 70%);
  filter:blur(5px);opacity:0;animation:smokeRise linear infinite}
.smoke i:nth-child(1){left:38%;animation-duration:3.8s}
.smoke i:nth-child(2){left:52%;animation-duration:4.6s;animation-delay:1.4s}
.smoke i:nth-child(3){left:45%;animation-duration:4.1s;animation-delay:2.6s}
@keyframes smokeRise{
  0%{transform:translate(0,0) scale(.8);opacity:0}
  12%{opacity:.5}
  60%{opacity:.28}
  100%{transform:translate(-9px,-84px) scale(1.9);opacity:0}}
/* rising sparks/embers */
.emberbox{position:absolute;inset:0;pointer-events:none}
.ember{position:absolute;bottom:12%;width:3px;height:3px;border-radius:50%;
  background:radial-gradient(circle,#ffd9a0,#ff8a30);filter:blur(.5px);animation:emberUp ease-out forwards}
@keyframes emberUp{from{transform:translate(0,0);opacity:.95}to{transform:translate(var(--ex),-72px);opacity:0}}
/* mesh door */
.fp-door{position:absolute;inset:0;z-index:5;
  background:
    repeating-linear-gradient(90deg,rgba(30,30,36,.9) 0 1px,transparent 1px 7px),
    repeating-linear-gradient(0deg,rgba(30,30,36,.9) 0 1px,transparent 1px 7px),
    rgba(10,10,14,.18);
  border:3px solid #23232a;border-radius:46% 46% 0 0/34% 34% 0 0;
  box-shadow:inset 0 0 10px rgba(0,0,0,.6);
  transform:translateX(-103%);transition:transform .85s cubic-bezier(.65,0,.35,1);
}
.fp-door::after{content:"";position:absolute;right:6px;top:52%;width:5px;height:12px;border-radius:3px;background:#3a3a44}
.fireplace.door-closed .fp-door{transform:translateX(0)}
/* log pile */
.fp-logpile{position:absolute;bottom:-6%;right:-27%;width:25%;height:17%;cursor:pointer}
.fp-logpile i{position:absolute;width:46%;aspect-ratio:1;border-radius:50%;
  background:
    repeating-radial-gradient(circle at 45% 42%, rgba(0,0,0,.22) 0 2px, transparent 2px 5px),
    radial-gradient(circle at 45% 42%,#7a5636 0 18%,#5a3d24 40%,#3a2615 70%,#241710);
  box-shadow:inset 0 0 0 2px rgba(0,0,0,.35)}
.fp-logpile i:nth-child(1){left:0;bottom:0}
.fp-logpile i:nth-child(2){left:44%;bottom:0}
.fp-logpile i:nth-child(3){left:22%;bottom:42%}
/* flying log + fire sparks */
.fly-log{position:fixed;z-index:54;width:34px;height:11px;border-radius:5px;pointer-events:none;
  background:linear-gradient(180deg,#4a3220,#2a1a10);
  animation:throwLog .75s cubic-bezier(.5,-0.1,.6,1) forwards}
@keyframes throwLog{
 0%{transform:translate(0,0) rotate(0)}
 55%{transform:translate(calc(var(--dx)*.55),calc(var(--dy)*.55 - 70px)) rotate(140deg)}
 100%{transform:translate(var(--dx),var(--dy)) rotate(300deg);opacity:.9}}
.fspark{position:fixed;z-index:55;width:4px;height:4px;border-radius:50%;pointer-events:none;
  background:radial-gradient(circle,#ffe9b0,#ff9a3a);animation:fsparkFly .8s ease-out forwards}
@keyframes fsparkFly{from{transform:translate(0,0);opacity:1}to{transform:translate(var(--dx),var(--dy));opacity:0}}
.firepool{position:absolute;left:7vw;bottom:3.5vh;width:24vw;height:8vh;border-radius:50%;
  background:radial-gradient(closest-side,rgba(255,160,60,.30),rgba(255,130,40,.10) 55%,transparent 76%);
  filter:blur(4px);mix-blend-mode:screen;opacity:0;pointer-events:none;transition:opacity .4s ease}

/* ============================================================
   THE CAT (silent — hearts only)
   ============================================================ */
.cat{position:absolute;left:calc(24% + 19vmin);bottom:9.5vh;width:150px;height:104px;
  pointer-events:auto;cursor:pointer}
.cat-body{position:absolute;left:34px;bottom:0;width:86px;height:62px;
  border-radius:54% 46% 42% 58%/72% 68% 32% 30%;
  background:radial-gradient(60% 45% at 42% 16%,#181820,#0b0b0f 62%,#070709);
  transform-origin:50% 100%;animation:catBreathe 4.2s ease-in-out infinite}
@keyframes catBreathe{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.022)}}
.cat-chest{position:absolute;left:22px;bottom:0;width:30px;height:46px;
  border-radius:48% 52% 10% 10%;background:#0a0a0e}
.cat-leg{position:absolute;bottom:0;width:9px;height:36px;background:#0a0a0e;border-radius:4px}
.cat-leg::after{content:"";position:absolute;bottom:0;left:-2px;width:13px;height:5px;
  border-radius:3px 4px 2px 2px;background:#0b0b0f}
.cat-leg.lg1{left:24px}
.cat-leg.lg2{left:40px;height:34px}
.cat-tail{position:absolute;left:88px;bottom:6px;width:56px;height:12px;border-radius:7px;
  background:#0b0b0f;transform-origin:6px center;animation:tailFlick 3.4s ease-in-out infinite}
.cat-tail::after{content:"";position:absolute;right:-3px;top:-7px;width:15px;height:15px;
  border-radius:50%;background:#0b0b0f}
@keyframes tailFlick{0%,100%{transform:rotate(12deg)}50%{transform:rotate(-16deg)}}
.cat.excited .cat-tail{animation-duration:1.1s}
.cat-head{position:absolute;left:6px;bottom:48px;width:46px;height:40px;
  border-radius:48% 48% 46% 46%;
  background:radial-gradient(60% 50% at 45% 20%,#17171e,#0a0a0e 70%);
  transform-origin:50% 90%;transition:transform .5s ease}
.cat.tilt-l .cat-head{transform:rotate(-5deg)}
.cat.tilt-r .cat-head{transform:rotate(5deg)}
.cat-ear{position:absolute;top:-10px;width:17px;height:17px;background:#0d0d12;
  clip-path:polygon(12% 100%,88% 100%,50% 0);transform-origin:50% 100%}
.cat-ear::after{content:"";position:absolute;left:28%;top:30%;width:44%;height:62%;
  background:#1e1418;clip-path:polygon(15% 100%,85% 100%,50% 0);opacity:.65}
.cat-ear.e-l{left:3px;transform:rotate(-7deg);animation:earTwitch 9s infinite}
.cat-ear.e-r{right:4px;transform:rotate(7deg)}
.cat.twitch .cat-ear.e-r{animation:earTwitch .9s 1}
@keyframes earTwitch{0%,91%,100%{transform:rotate(-7deg)}93%{transform:rotate(-19deg)}96%{transform:rotate(-5deg)}}
.cat-eye{position:absolute;top:16px;width:7px;height:8px;
  border-radius:50% 50% 50% 50%/60% 60% 40% 40%;
  background:radial-gradient(circle,#d8ffa8,#7fd45a 65%,rgba(127,212,90,0));
  box-shadow:0 0 7px 1px rgba(150,235,110,.65);
  opacity:calc(1 - var(--on)*.92);transition:opacity .8s ease,transform .3s ease;
  animation:blink 5.5s infinite}
.cat-eye.ey-l{left:9px}
.cat-eye.ey-r{left:27px;animation-delay:.15s}
.cat.pet .cat-eye{animation:none;transform:scaleY(.32)}
@keyframes blink{0%,92%,100%{transform:scaleY(1)}94%{transform:scaleY(.08)}96%{transform:scaleY(1)}}
.whisk{position:absolute;left:-13px;width:15px;height:1px;background:rgba(255,255,255,.08)}
.whisk.wk1{top:21px;transform:rotate(-9deg)}
.whisk.wk2{top:24px}
.whisk.wk3{top:27px;transform:rotate(9deg)}
.cat-shadow{position:absolute;left:6%;bottom:-7px;width:90%;height:12px;border-radius:50%;
  background:radial-gradient(closest-side,rgba(0,0,0,.65),transparent);
  opacity:var(--on);transition:opacity .6s;filter:blur(2px)}
.heart{position:fixed;z-index:55;width:9px;height:9px;pointer-events:none;
  background:#e0708a;transform:rotate(-45deg);animation:heartFloat 1.3s ease-out forwards}
.heart::before,.heart::after{content:"";position:absolute;width:9px;height:9px;border-radius:50%;background:#e0708a}
.heart::before{top:-4.5px;left:0}
.heart::after{left:4.5px;top:0}
@keyframes heartFloat{
  from{opacity:.95;transform:rotate(-45deg) translate(0,0) scale(.7)}
  to{opacity:0;transform:rotate(-45deg) translate(10px,-52px) scale(1.25)}}

/* ============================================================
   DUST MOTES
   ============================================================ */
.motes{position:absolute;top:calc(var(--lampH)*.70);left:24%;transform:translateX(-50%);
  width:min(74vmin,580px);height:calc(92vh - var(--lampH)*.70);pointer-events:none;
  opacity:0;transition:opacity .4s ease;will-change:transform}
body.lamp-on .motes{opacity:var(--lum)}
.mote{position:absolute;border-radius:50%;background:rgba(255,232,180,.85);filter:blur(1px);
  animation:drift linear infinite}
@keyframes drift{0%{transform:translateY(20px);opacity:0}12%{opacity:.75}80%{opacity:.4}100%{transform:translateY(-75px);opacity:0}}

/* ============================================================
   THE LAMP
   ============================================================ */
.lamp-assembly{position:absolute;top:0;left:calc(24% - 120px);width:240px;height:100vh;
  transform:rotate(var(--sway));
  transform-origin:50% 0;pointer-events:none;user-select:none;will-change:transform}
@keyframes flicker{
  0%{opacity:0}6%{opacity:.9}12%{opacity:.15}20%{opacity:1}28%{opacity:.35}
  36%{opacity:.95}46%{opacity:.55}58%{opacity:1}70%{opacity:.8}100%{opacity:1}}
.beam{position:absolute;top:calc(var(--lampH)*.62);left:50%;transform:translateX(-50%);
  width:min(74vmin,580px);height:calc(90vh - var(--lampH)*.62);pointer-events:none;
  clip-path:polygon(45.5% 0,54.5% 0,100% 100%,0 100%);
  background:linear-gradient(180deg,
    rgba(255,226,164,.40) 0%,rgba(255,216,144,.17) 45%,
    rgba(255,208,134,.05) 80%,rgba(255,200,120,0) 100%);
  opacity:0;transition:opacity .22s ease;
  -webkit-mask-image:linear-gradient(90deg,transparent 0%,#000 10%,#000 90%,transparent 100%);
  mask-image:linear-gradient(90deg,transparent 0%,#000 10%,#000 90%,transparent 100%)}
.beam-core{position:absolute;top:calc(var(--lampH)*.62);left:50%;transform:translateX(-50%);
  width:min(74vmin,580px);height:calc(90vh - var(--lampH)*.62);pointer-events:none;
  clip-path:polygon(48.5% 0,51.5% 0,84% 100%,16% 100%);
  background:linear-gradient(180deg,
    rgba(255,236,190,.34) 0%,rgba(255,220,150,.10) 55%,rgba(255,214,140,0) 92%);
  opacity:0;transition:opacity .22s ease;
  -webkit-mask-image:linear-gradient(90deg,transparent 0%,#000 16%,#000 84%,transparent 100%);
  mask-image:linear-gradient(90deg,transparent 0%,#000 16%,#000 84%,transparent 100%)}
body.lamp-on .beam,body.lamp-on .beam-core{opacity:var(--lum);animation:flicker .95s linear}
.fixture{display:block;height:var(--lampH);width:auto;margin:0 auto;overflow:visible;position:relative;z-index:2}
.fixture .rib{fill:none;stroke:rgba(255,255,255,.05);stroke-width:1}
.fixture .lead{stroke:#55555e;stroke-width:1.4;fill:none;transition:stroke .3s}
.fixture .fil{fill:none;stroke:#4a4a52;stroke-width:1.3;transition:stroke .25s,filter .25s}
.fixture .clickable{cursor:pointer}
.fixture .onlayer{opacity:0;transition:opacity .3s ease}
.fixture.on .onlayer{opacity:1}
.fixture.on .fil{stroke:#ffb347;
  filter:drop-shadow(0 0 4px rgba(255,170,60,.95)) drop-shadow(0 0 10px rgba(255,150,40,.5))}
.fixture.on .lead{stroke:#8a7454}
.chainG{transform-box:fill-box;transform-origin:top center;
  transform:rotate(calc(var(--sway)*-1.3))}
.chain-hit{position:absolute;top:calc(var(--lampH)*.58);left:calc(50% + var(--lampH)*.10);
  width:66px;height:calc(var(--lampH)*.36);cursor:grab;touch-action:none;
  pointer-events:auto;z-index:6;outline:none}
.lamp-assembly.dragging .chain-hit{cursor:grabbing}
.chain-pull{position:absolute;top:calc(var(--lampH)*.60);left:calc(50% + var(--lampH)*.19);
  width:3px;height:calc(var(--lampH)*.20);pointer-events:none;z-index:5;
  background:repeating-linear-gradient(180deg,#6a6a74 0 4px,#3a3a42 4px 8px);
  transform:translateY(var(--pull,0px));
  transition:transform .28s cubic-bezier(.3,1.7,.5,1)}
.chain-pull::after{content:"";position:absolute;bottom:-12px;left:50%;transform:translateX(-50%);
  width:12px;height:12px;border-radius:50%;
  background:radial-gradient(circle at 35% 30%,#a8905e,#3f3626)}
.lamp-assembly.dragging .chain-pull{transition:none}
.bulb-glow{position:absolute;top:calc(var(--lampH)*.70 - 110px);left:50%;transform:translateX(-50%);
  width:230px;height:230px;border-radius:50%;pointer-events:none;z-index:3;
  background:radial-gradient(circle,rgba(255,226,160,.45),rgba(255,200,120,.18) 45%,transparent 72%);
  opacity:0;transition:opacity .25s ease}
body.lamp-on .bulb-glow{opacity:var(--lum)}
.spark{position:absolute;top:calc(var(--lampH)*.72);left:50%;width:4px;height:4px;border-radius:50%;
  background:radial-gradient(circle,#fff3d0,#ffb64d);pointer-events:none;z-index:7;
  animation:sparkFly .9s ease-out forwards}
@keyframes sparkFly{from{transform:translate(0,0) scale(1);opacity:1}
  to{transform:translate(var(--dx),var(--dy)) scale(.15);opacity:0}}
.moth-system{position:absolute;top:calc(var(--lampH)*.70);left:50%;width:0;height:0;
  opacity:0;transition:opacity .9s ease .9s;pointer-events:none;z-index:4}
body:not(.lamp-on) .moth-system{transition-delay:0s}
body.lamp-on .moth-system{opacity:calc(var(--lum)*.95)}
.moth-bob{animation:mothBob 2.8s ease-in-out infinite alternate}
@keyframes mothBob{from{transform:translateY(-5px)}to{transform:translateY(6px)}}
.moth-orbit{animation:mothOrbit 6.5s linear infinite}
@keyframes mothOrbit{from{transform:rotate(0)}to{transform:rotate(360deg)}}
.moth{position:absolute;left:44px;top:-4px;width:8px;height:8px}
.moth b{position:absolute;top:1px;width:7px;height:5px;border-radius:60% 60% 40% 40%;
  background:radial-gradient(circle at 40% 40%,#efe3c2,#b3a37e)}
.moth b.wl{left:-5px;transform-origin:right center;animation:flapL .16s ease-in-out infinite alternate}
.moth b.wr{right:-5px;transform-origin:left center;animation:flapR .16s ease-in-out infinite alternate}
@keyframes flapL{from{transform:rotate(-38deg)}to{transform:rotate(-6deg)}}
@keyframes flapR{from{transform:rotate(38deg)}to{transform:rotate(6deg)}}
.moth i{position:absolute;left:3px;top:0;width:2px;height:7px;border-radius:2px;background:#8f8160}

.roomglow{position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;
  background:
    radial-gradient(58% 44% at 24% 30%,rgba(255,198,122,.14),transparent 70%),
    radial-gradient(120% 80% at 24% 102%,rgba(255,190,110,.08),transparent 60%);
  opacity:0;transition:opacity .4s ease .08s}
body.lamp-on .roomglow{opacity:var(--lum)}

/* ============================================================
   THE CLOCK PLATE
   ============================================================ */
.timeplate{position:absolute;right:9vw;top:36%;transform:translateY(-50%);text-align:right;z-index:6;
  transition:right 3s ease,top 3s ease;pointer-events:none}
.timeplate::before{content:"";position:absolute;inset:-34% -22%;pointer-events:none;
  background:radial-gradient(closest-side,rgba(255,205,140,.16),transparent 72%);
  filter:blur(8px);opacity:var(--on);transition:opacity .8s ease}
.time{font-size:clamp(46px,8vmin,92px);font-weight:200;letter-spacing:.08em;color:#767d8c;
  line-height:1;font-family:"Segoe UI Light","Segoe UI",system-ui,sans-serif;
  transition:color .6s ease,text-shadow .6s ease}
.date{margin-top:10px;font-size:clamp(10px,1.5vmin,14px);letter-spacing:.34em;
  text-transform:uppercase;color:#4c515c;transition:color .6s ease}
body.lamp-on .time{color:#ffe6bd;text-shadow:0 0 28px rgba(255,205,140,.35)}
body.lamp-on .date{color:#b39a72}

/* ============================================================
   OVERLAYS / UI
   ============================================================ */
.vignette{position:absolute;inset:0;pointer-events:none;z-index:20;
  background:radial-gradient(120% 100% at 50% 45%,transparent 55%,rgba(0,0,0,.5))}
.grain{position:absolute;inset:-20%;pointer-events:none;z-index:21;opacity:.05;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.uirow{position:fixed;top:12px;right:12px;display:flex;gap:8px;z-index:40;transition:opacity .6s}
.uirow button{border:1px solid rgba(255,255,255,.1);background:rgba(18,18,24,.55);color:#cfcfd6;
  border-radius:10px;padding:8px 11px;cursor:pointer;backdrop-filter:blur(4px);transition:.3s;
  display:flex;align-items:center;justify-content:center}
.uirow button:hover{border-color:rgba(255,205,140,.4)}
.uirow button.active{border-color:rgba(255,205,140,.6);color:#ffd9a0;box-shadow:0 0 12px rgba(255,190,110,.2)}
.uirow button svg{display:block;width:16px;height:16px;fill:none;stroke:currentColor;
  stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
#soundBtn .slash{display:none}
#soundBtn.muted .waves{display:none}
#soundBtn.muted .slash{display:block}
.hintbar{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);z-index:40;
  font-size:.7rem;letter-spacing:.14em;color:#5c5c66;text-transform:uppercase;
  white-space:nowrap;transition:opacity .6s}
body.idle .uirow,body.idle .hintbar{opacity:0;pointer-events:none}
.boot{position:fixed;inset:0;z-index:60;background:#010102;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:14px;transition:opacity 1s ease}
.boot.done{opacity:0;pointer-events:none}
.boot h1{font-size:1.6rem;letter-spacing:.5em;text-indent:.5em;text-transform:uppercase;color:#c8b48a;
  animation:bootGlow 2.4s ease-in-out infinite alternate}
@keyframes bootGlow{from{text-shadow:0 0 6px rgba(255,205,140,.1)}to{text-shadow:0 0 26px rgba(255,205,140,.5)}}
.boot p{color:#5a5a64;font-size:.8rem;letter-spacing:.14em}

body.lowpower .floorpool{filter:blur(3px)}
body.lowpower .rug-light{filter:blur(2px)}
body.lowpower .motes .mote:nth-child(even){display:none}
body.lowpower .moonshaft{filter:none}

@media (max-width:820px){
  .lamp-assembly{left:calc(50% - 120px)}
  .motes{left:50%}
  .rug{left:50%}
  .cat{left:calc(50% + 12vmin)}
  .moonshaft{left:2vw;width:70vw;clip-path:polygon(2.86% 0,62.86% 0,92% 100%,20% 100%)}
  .daypool{left:10vw;width:70vw}
  .frame,.clockw,.fireplace,.firepool{display:none}
  .plant{left:6vw}
  .window{left:4vw;width:42vw;height:22vh}
  .timeplate{right:50%;transform:translate(50%,-50%);top:58%;text-align:center}
}
</style>
</head>
<body>
<div class="scene">
  <div class="scene-stars"></div>

  <div class="layer-far">
    <div class="window" id="windowEl">
      <div class="sky" id="skyA" style="opacity:1"></div>
      <div class="sky" id="skyB" style="opacity:0"></div>
      <div class="nightbits" id="nightbits">
        <div class="win-stars"></div>
        <div class="shoot"></div>
        <div class="shoot s2"></div>
      </div>
      <div class="sun" id="sunEl"></div>
      <div class="moon" id="moonEl"></div>
      <div class="cloud c1"></div>
      <div class="cloud c2"></div>
      <div class="cloud c3"></div>
      <div class="win-sheen"></div>
      <div class="bars-v"></div>
      <div class="bars-h"></div>
      <div class="curtain cl"></div>
      <div class="curtain cr"></div>
    </div>
    <div class="frame f1" id="frame1">
      <div class="art">
        <div class="artsky"></div><div class="sunp"></div>
        <div class="mtn m1"></div><div class="mtn m2"></div>
        <div class="glass"></div>
      </div>
    </div>
    <div class="frame f2" id="frame2">
      <div class="art">
        <div class="seasky"></div><div class="moon2"></div><div class="ref"></div>
        <div class="wave w1"></div><div class="wave w2"></div>
        <div class="glass"></div>
      </div>
    </div>
    <div class="clockw" id="clockEl">
      <div class="clock-face">
        <div class="hand h" id="hourH"></div>
        <div class="hand m" id="minH"></div>
        <div class="hand s" id="secH"></div>
        <div class="clock-pin"></div>
      </div>
      <div class="clock-case"><div class="pendulum"></div></div>
    </div>
  </div>

  <div class="moonshaft" id="shaft"></div>
  <div class="daylight" id="daylight"></div>
  <div class="roomglow" id="roomglow"></div>
  <div class="floor"><div class="floor-sheen" id="floorSheen"></div></div>
  <div class="baseboard"></div>
  <div class="rug"></div>
  <div class="rug-light" id="rugLight"></div>
  <div class="floorpool" id="floorpool"></div>
  <div class="daypool" id="daypool"></div>
  <div class="firepool" id="firepool"></div>

  <div class="layer-mid">
    <div class="plant" id="plantEl">
      <div class="plant-leaves"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
      <div class="plant-soil"></div>
      <div class="plant-rim"></div>
      <div class="plant-pot"></div>
    </div>
  </div>

  <div class="fireplace" id="fireplaceEl">
    <div class="fp-mantle">
      <div class="fp-book b1"></div>
      <div class="fp-book b2"></div>
      <div class="fp-book b3"></div>
      <div class="fp-candle"></div>
    </div>
    <div class="fp-body" id="fpBody">
      <div class="fp-mouth">
        <div class="fp-glow" id="fpGlow"></div>
        <div class="logs" id="fpLogs"><i></i><i></i><i></i><i></i></div>
        <div class="fire" id="fire">
          <i class="fl f0"></i>
          <i class="fl f1"></i>
          <i class="fl f2"></i>
          <i class="fl f3"></i>
          <i class="fl f4"></i>
          <i class="fl f5"></i>
          <i class="fl fc"></i>
          <div class="coals"><b></b><b></b><b></b><b></b><b></b><b></b><b></b></div>
          <div class="smoke"><i></i><i></i><i></i></div>
          <div class="emberbox" id="emberbox"></div>
        </div>
        <div class="fp-door"></div>
      </div>
    </div>
    <div class="fp-hearth"></div>
    <div class="fp-logpile" id="logPile"><i></i><i></i><i></i></div>
  </div>

  <div class="cat" id="catEl" aria-label="the cat — pet it">
    <div class="cat-tail"></div>
    <div class="cat-body"></div>
    <div class="cat-chest"></div>
    <div class="cat-leg lg1"></div>
    <div class="cat-leg lg2"></div>
    <div class="cat-head">
      <div class="cat-ear e-l"></div><div class="cat-ear e-r"></div>
      <div class="cat-eye ey-l"></div><div class="cat-eye ey-r"></div>
      <div class="whisk wk1"></div><div class="whisk wk2"></div><div class="whisk wk3"></div>
    </div>
    <div class="cat-shadow"></div>
  </div>

  <div class="motes" id="motesLayer"></div>

  <div class="lamp-assembly" id="lampAssembly">
    <div class="beam" id="beam"></div>
    <div class="beam-core"></div>
    <svg class="fixture" id="fixture" viewBox="0 0 240 340" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="metalV" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#17171b"/><stop offset=".45" stop-color="#3c3c44"/>
          <stop offset=".55" stop-color="#4a4a52"/><stop offset="1" stop-color="#141417"/>
        </linearGradient>
        <linearGradient id="shadeG" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#101013"/><stop offset=".18" stop-color="#2c2c33"/>
          <stop offset=".34" stop-color="#45454e"/><stop offset=".5" stop-color="#232328"/>
          <stop offset=".72" stop-color="#39393f"/><stop offset="1" stop-color="#0e0e11"/>
        </linearGradient>
        <linearGradient id="shadeWarm" x1="0" y1="1" x2="0" y2="0">
          <stop offset="0" stop-color="#ffbe78" stop-opacity=".55"/>
          <stop offset=".5" stop-color="#ffbe78" stop-opacity=".12"/>
          <stop offset="1" stop-color="#ffbe78" stop-opacity="0"/>
        </linearGradient>
        <radialGradient id="mouthGlow" cx=".5" cy=".5" r=".5">
          <stop offset="0" stop-color="#ffe7bd"/><stop offset=".55" stop-color="#ffbe76" stop-opacity=".85"/>
          <stop offset="1" stop-color="#ffbe76" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="halo" cx=".5" cy=".5" r=".5">
          <stop offset="0" stop-color="#ffdf9e" stop-opacity=".9"/>
          <stop offset=".4" stop-color="#ffc46e" stop-opacity=".35"/>
          <stop offset="1" stop-color="#ffc46e" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="glassOn" cx=".5" cy=".42" r=".65">
          <stop offset="0" stop-color="#fff8e0"/><stop offset=".45" stop-color="#ffd98f"/>
          <stop offset=".8" stop-color="#ffb64d"/><stop offset="1" stop-color="#f09a34"/>
        </radialGradient>
        <linearGradient id="glassOff" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#3a3a41"/><stop offset=".6" stop-color="#232327"/>
          <stop offset="1" stop-color="#1a1a1e"/>
        </linearGradient>
        <linearGradient id="brass" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#8f7f5a"/><stop offset=".5" stop-color="#5c5138"/>
          <stop offset="1" stop-color="#3a3324"/>
        </linearGradient>
      </defs>

      <path d="M104 0 h32 v5 c0 4 -3 6 -7 7 h-18 c-4 -1 -7 -3 -7 -7 z" fill="#1c1c21"/>
      <path d="M106 12 h28 l-4 8 h-20 z" fill="#141419"/>
      <line x1="120" y1="20" x2="120" y2="128" stroke="#232329" stroke-width="4"/>
      <line x1="120" y1="20" x2="120" y2="128" stroke="#3b3b43" stroke-width="4" stroke-dasharray="5 5"/>
      <line x1="119" y1="20" x2="119" y2="128" stroke="rgba(255,255,255,.08)" stroke-width="1"/>
      <rect x="112" y="126" width="16" height="9" rx="3" fill="#2a2a30"/>
      <rect x="109" y="133" width="22" height="15" rx="4" fill="url(#metalV)"/>
      <line x1="109" y1="141" x2="131" y2="141" stroke="rgba(0,0,0,.5)" stroke-width="1"/>
      <path id="shadeDome" class="clickable"
        d="M120 146 C 74 148, 44 172, 36 212 L 204 212 C 196 172, 166 148, 120 146 Z" fill="url(#shadeG)"/>
      <path class="rib" d="M120 146 C 84 150, 58 176, 46 212"/>
      <path class="rib" d="M120 146 C 96 150, 76 178, 68 212"/>
      <path class="rib" d="M120 146 C 112 152, 104 182, 100 212"/>
      <path class="rib" d="M120 146 C 128 152, 136 182, 140 212"/>
      <path class="rib" d="M120 146 C 144 150, 164 178, 172 212"/>
      <path class="rib" d="M120 146 C 156 150, 182 176, 194 212"/>
      <path d="M84 162 C 72 174, 64 192, 60 208" stroke="rgba(255,255,255,.09)" stroke-width="6" fill="none" opacity=".5"/>
      <path class="onlayer" d="M120 146 C 74 148, 44 172, 36 212 L 204 212 C 196 172, 166 148, 120 146 Z" fill="url(#shadeWarm)"/>
      <ellipse cx="120" cy="212" rx="84" ry="7" fill="url(#metalV)"/>
      <ellipse cx="120" cy="211" rx="84" ry="6.4" fill="none" stroke="rgba(255,255,255,.09)"/>
      <ellipse cx="120" cy="212" rx="76" ry="5.4" fill="#050506"/>
      <ellipse class="onlayer" cx="120" cy="213" rx="76" ry="6" fill="url(#mouthGlow)"/>
      <path class="lead" d="M114 214 L111 232"/>
      <path class="lead" d="M126 214 L129 232"/>
      <path id="bulbGlass" class="clickable"
        d="M120 214 C 105 218, 100 231, 102 241 C 104 253, 111 260, 120 262 C 129 260, 136 253, 138 241 C 140 231, 135 218, 120 214 Z"
        fill="url(#glassOff)" stroke="rgba(255,255,255,.06)"/>
      <path class="onlayer"
        d="M120 214 C 105 218, 100 231, 102 241 C 104 253, 111 260, 120 262 C 129 260, 136 253, 138 241 C 140 231, 135 218, 120 214 Z"
        fill="url(#glassOn)"/>
      <path class="fil" d="M111 232 L114 238 L117 232 L120 238 L123 232 L126 238 L129 232"/>
      <ellipse cx="111" cy="228" rx="4" ry="8" fill="rgba(255,255,255,.13)" transform="rotate(18 111 228)"/>
      <circle class="onlayer" cx="120" cy="240" r="58" fill="url(#halo)"/>
      <g class="chainG">
        <line x1="188" y1="214" x2="188" y2="266" stroke="#5a5a64" stroke-width="2" stroke-dasharray="3 3"/>
        <circle cx="188" cy="272" r="5.5" fill="url(#brass)" stroke="rgba(0,0,0,.5)"/>
      </g>
    </svg>
    <div class="chain-pull"></div>
    <div class="chain-hit" id="chainHit" role="button" aria-label="Toggle the lamp" tabindex="0"></div>
    <div class="bulb-glow"></div>
    <div class="moth-system">
      <div class="moth-bob"><div class="moth-orbit">
        <div class="moth"><b class="wl"></b><b class="wr"></b><i></i></div>
      </div></div>
    </div>
  </div>

  <div class="timeplate" id="timeplate">
    <div class="time" id="timeText">00:00</div>
    <div class="date" id="dateText">—</div>
  </div>

  <div class="vignette"></div>
  <div class="grain"></div>
</div>

<div class="uirow">
  <button id="soundBtn" title="sound on/off">
    <svg viewBox="0 0 16 16" aria-hidden="true">
      <path d="M2.8 6.2h2.4L8.6 3.6v8.8L5.2 9.8H2.8z" fill="currentColor" stroke="none"/>
      <path class="waves" d="M10.6 5.6a3.4 3.4 0 0 1 0 4.8M12.3 3.9a5.8 5.8 0 0 1 0 8.2"/>
      <line class="slash" x1="3" y1="13.2" x2="13.4" y2="2.8"/>
    </svg>
  </button>
  <button id="curtainBtn" title="open/close curtains (C)">
    <svg viewBox="0 0 16 16" aria-hidden="true">
      <rect x="2.6" y="2.6" width="10.8" height="10.8" rx="1"/>
      <path d="M8 2.6v10.8M2.6 8h10.8"/>
    </svg>
  </button>
  <button id="ssBtn" title="fullscreen + keep screen awake (F)">
    <svg viewBox="0 0 16 16" aria-hidden="true">
      <path d="M2.6 6V2.6H6M10 2.6h3.4V6M13.4 10v3.4H10M6 13.4H2.6V10"/>
    </svg>
  </button>
</div>
<div class="hintbar" id="hintbar">chain = light &nbsp;·&nbsp; window = curtains &nbsp;·&nbsp; logs = feed fire &nbsp;·&nbsp; pet the cat</div>

<div class="boot" id="boot">
  <h1>Lamp Room</h1>
  <p>ambient screensaver — real sky, warm hearth</p>
</div>

<script>
(function(){
  "use strict";
  var body=document.body, root=body;
  var fixture=document.getElementById('fixture'),
      boot=document.getElementById('boot'),
      floorpool=document.getElementById('floorpool'),
      rugLight=document.getElementById('rugLight'),
      floorSheen=document.getElementById('floorSheen'),
      shaft=document.getElementById('shaft'),
      daylightEl=document.getElementById('daylight'),
      daypool=document.getElementById('daypool'),
      nightbits=document.getElementById('nightbits'),
      windowEl=document.getElementById('windowEl'),
      skyA=document.getElementById('skyA'),
      skyB=document.getElementById('skyB'),
      sunEl=document.getElementById('sunEl'),
      moonEl=document.getElementById('moonEl'),
      catEl=document.getElementById('catEl'),
      fireplaceEl=document.getElementById('fireplaceEl'),
      fpBody=document.getElementById('fpBody'),
      fpGlow=document.getElementById('fpGlow'),
      fireEl=document.getElementById('fire'),
      fpLogs=document.getElementById('fpLogs'),
      emberbox=document.getElementById('emberbox'),
      logPile=document.getElementById('logPile'),
      firepoolEl=document.getElementById('firepool'),
      timeplate=document.getElementById('timeplate'),
      soundBtn=document.getElementById('soundBtn'),
      curtainBtn=document.getElementById('curtainBtn'),
      ssBtn=document.getElementById('ssBtn'),
      assembly=document.getElementById('lampAssembly'),
      motesLayer=document.getElementById('motesLayer'),
      chainHit=document.getElementById('chainHit');
  var lumVal=1;

  /* ================= sound ================= */
  var AC=null, soundOn=(localStorage.getItem('lr-sound')!=='0');
  function paintSound(){soundBtn.classList.toggle('muted',!soundOn);}
  paintSound();
  soundBtn.addEventListener('click',function(){
    ensureAC();
    soundOn=!soundOn;localStorage.setItem('lr-sound',soundOn?'1':'0');paintSound();wake();
  });
  function ensureAC(){
    if(!AC){try{AC=new (window.AudioContext||window.webkitAudioContext)();}catch(e){}}
    if(AC&&AC.state==='suspended'){try{AC.resume();}catch(e){}}
  }
  document.addEventListener('pointerdown',ensureAC,{once:true});
  function playTick(turningOn){
    ensureAC();
    if(!soundOn||!AC)return;
    try{
      var t=AC.currentTime;
      var buf=AC.createBuffer(1,Math.floor(AC.sampleRate*0.03),AC.sampleRate);
      var d=buf.getChannelData(0);
      for(var i=0;i<d.length;i++){d[i]=(Math.random()*2-1)*Math.pow(1-i/d.length,2);}
      var src=AC.createBufferSource();src.buffer=buf;
      var bp=AC.createBiquadFilter();bp.type='bandpass';bp.frequency.value=turningOn?1800:1200;bp.Q.value=1.1;
      var g=AC.createGain();g.gain.setValueAtTime(0.35,t);g.gain.exponentialRampToValueAtTime(0.001,t+0.05);
      src.connect(bp);bp.connect(g);g.connect(AC.destination);src.start(t);
      if(turningOn){
        var o=AC.createOscillator();o.type='sine';
        o.frequency.setValueAtTime(120,t);o.frequency.exponentialRampToValueAtTime(58,t+0.13);
        var og=AC.createGain();og.gain.setValueAtTime(0.1,t);og.gain.exponentialRampToValueAtTime(0.001,t+0.16);
        o.connect(og);og.connect(AC.destination);o.start(t);o.stop(t+0.17);
      }
    }catch(e){}
  }
  function doorClick(){
    ensureAC();if(!soundOn||!AC)return;
    try{
      var t=AC.currentTime;
      var o=AC.createOscillator();o.type='square';o.frequency.value=210;
      var lp=AC.createBiquadFilter();lp.type='lowpass';lp.frequency.value=900;
      var g=AC.createGain();g.gain.setValueAtTime(0.09,t);
      g.gain.exponentialRampToValueAtTime(0.001,t+0.08);
      o.connect(lp);lp.connect(g);g.connect(AC.destination);o.start(t);o.stop(t+0.09);
    }catch(e){}
  }
  function playToss(){
    ensureAC();if(!soundOn||!AC)return;
    try{
      var t=AC.currentTime;
      var buf=AC.createBuffer(1,Math.floor(AC.sampleRate*0.3),AC.sampleRate);
      var d=buf.getChannelData(0);
      for(var i=0;i<d.length;i++){d[i]=(Math.random()*2-1)*0.6;}
      var src=AC.createBufferSource();src.buffer=buf;
      var bp=AC.createBiquadFilter();bp.type='bandpass';bp.Q.value=1.2;
      bp.frequency.setValueAtTime(450,t);bp.frequency.linearRampToValueAtTime(950,t+0.28);
      var g=AC.createGain();g.gain.setValueAtTime(0.0001,t);
      g.gain.exponentialRampToValueAtTime(0.09,t+0.06);
      g.gain.exponentialRampToValueAtTime(0.0001,t+0.3);
      src.connect(bp);bp.connect(g);g.connect(AC.destination);src.start(t);
    }catch(e){}
  }
  function thud(){
    ensureAC();if(!soundOn||!AC)return;
    try{
      var t=AC.currentTime;
      var o=AC.createOscillator();o.type='sine';
      o.frequency.setValueAtTime(120,t);o.frequency.exponentialRampToValueAtTime(55,t+0.16);
      var g=AC.createGain();g.gain.setValueAtTime(0.3,t);
      g.gain.exponentialRampToValueAtTime(0.001,t+0.2);
      o.connect(g);g.connect(AC.destination);o.start(t);o.stop(t+0.22);
      var buf=AC.createBuffer(1,Math.floor(AC.sampleRate*0.05),AC.sampleRate);
      var d=buf.getChannelData(0);
      for(var i=0;i<d.length;i++){d[i]=(Math.random()*2-1)*Math.pow(1-i/d.length,2);}
      var src=AC.createBufferSource();src.buffer=buf;
      var lp=AC.createBiquadFilter();lp.type='lowpass';lp.frequency.value=500;
      var g2=AC.createGain();g2.gain.setValueAtTime(0.16,t);
      g2.gain.exponentialRampToValueAtTime(0.001,t+0.08);
      src.connect(lp);lp.connect(g2);g2.connect(AC.destination);src.start(t);
    }catch(e){}
  }
  function crackleOnce(){
    if(!soundOn||!AC||AC.state!=='running')return;
    try{
      var t=AC.currentTime;
      var buf=AC.createBuffer(1,Math.floor(AC.sampleRate*0.03),AC.sampleRate);
      var d=buf.getChannelData(0);
      for(var i=0;i<d.length;i++){d[i]=(Math.random()*2-1)*Math.pow(1-i/d.length,2);}
      var src=AC.createBufferSource();src.buffer=buf;
      var bp=AC.createBiquadFilter();bp.type='bandpass';
      bp.frequency.value=600+Math.random()*1400;bp.Q.value=1.5;
      var g=AC.createGain();g.gain.setValueAtTime(0.05+Math.random()*0.04,t);
      g.gain.exponentialRampToValueAtTime(0.001,t+0.05);
      src.connect(bp);bp.connect(g);g.connect(AC.destination);src.start(t);
    }catch(e){}
  }
  function crackleLoop(){
    setTimeout(function(){crackleOnce();crackleLoop();},2200+Math.random()*5000);
  }
  crackleLoop();

  /* ================= geometry ================= */
  var W=innerWidth,H=innerHeight,baseX=0,lampHpx=0;
  var mq=matchMedia('(max-width:820px)');
  function measure(){
    W=innerWidth;H=innerHeight;
    baseX=W*(mq.matches?0.5:0.24);
    lampHpx=H*0.36;
  }
  addEventListener('resize',measure);measure();

  /* ================= physics ================= */
  var th=0.05,w=0,G=9.8,LEN=1.7,DAMP=0.45,pushDir=1,last=performance.now();
  var curBulbX=0,curBulbY=0;
  function impulse(s){w+=s*pushDir;pushDir*=-1;}

  var perfState=0,perfCount=0,perfSum=0;
  function perfCheck(dtMs){
    if(!body.classList.contains('lamp-on')||body.classList.contains('lowpower')){perfState=0;return;}
    if(perfState===0){perfState=1;perfCount=0;return;}
    if(perfState===1){perfCount++;if(perfCount>50){perfState=2;perfCount=0;perfSum=0;}return;}
    if(perfState===2){
      perfSum+=dtMs;perfCount++;
      if(perfCount>=60){
        perfState=3;
        if(perfSum/60>23)body.classList.add('lowpower');
      }
    }
  }

  function physics(now){
    var dt=Math.min((now-last)/1000,0.033);last=now;
    perfCheck(dt*1000);
    var acc=-(G/LEN)*Math.sin(th)-DAMP*w;
    w+=acc*dt;th+=w*dt;
    w+=Math.sin(now*0.0004)*0.00004+(Math.random()-0.5)*0.00035;
    if(Math.abs(th)>0.5){th=0.5*(th>0?1:-1);w*=-0.3;}
    var deg=th*180/Math.PI;
    var sinT=Math.sin(th);
    root.style.setProperty('--sway',deg.toFixed(3)+'deg');
    curBulbX=baseX-sinT*lampHpx*0.70;
    curBulbY=lampHpx*0.70;
    motesLayer.style.transform=
      'translate3d(calc(-50% + '+Math.round(-sinT*lampHpx*0.70)+'px),0,0)';
    floorpool.style.transform='translate3d('+Math.round(baseX-sinT*H*0.66)+'px,0,0) translateX(-50%)';
    rugLight.style.transform='translate3d('+Math.round(baseX-sinT*H*0.60)+'px,0,0) translateX(-50%)';
    floorSheen.style.transform='translate3d('+Math.round(-sinT*H*0.28)+'px,0,0)';
    requestAnimationFrame(physics);
  }
  requestAnimationFrame(physics);

  /* ============================================================
     THE REAL SKY
     ============================================================ */
  var RAD=Math.PI/180;
  var lat=null,lng=null;
  var dayFactor=0;

  function clamp(v,a,b){return v<a?a:(v>b?b:v);}
  function smooth(a,b,x){var t=clamp((x-a)/(b-a),0,1);return t*t*(3-2*t);}
  function mixC(a,b,t){return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t];}
  function rgb(c){return 'rgb('+(c[0]|0)+','+(c[1]|0)+','+(c[2]|0)+')';}
  function dayOfYear(d){return Math.floor((d-new Date(d.getFullYear(),0,0))/864e5);}

  function altAz(solarH,latDeg,decl){
    var Hr=(solarH-12)*15*RAD, latR=latDeg*RAD;
    var sinAlt=Math.sin(latR)*Math.sin(decl)+Math.cos(latR)*Math.cos(decl)*Math.cos(Hr);
    sinAlt=clamp(sinAlt,-1,1);
    var alt=Math.asin(sinAlt);
    var cosAz=(Math.sin(decl)-sinAlt*Math.sin(latR))/((Math.cos(alt)*Math.cos(latR))||1e-6);
    var az=Math.acos(clamp(cosAz,-1,1));
    if(Hr>0)az=2*Math.PI-az;
    return {alt:alt/RAD,az:az/RAD};
  }
  function sunNow(d,la,ln){
    var N=dayOfYear(d);
    var B=2*Math.PI*(N-81)/364;
    var eot=9.87*Math.sin(2*B)-7.53*Math.cos(B)-1.5*Math.sin(B);
    var decl=23.44*Math.sin(2*Math.PI*(284+N)/365)*RAD;
    var tzH=-d.getTimezoneOffset()/60;
    var solar=d.getHours()+d.getMinutes()/60+d.getSeconds()/60+eot/60+(ln/15)-tzH;
    return {sun:altAz(solar,la,decl),moon:altAz(solar+12,la,decl),decl:decl};
  }

  var SKY=[
    [-18,[5,7,15],[9,13,30],[13,19,42]],
    [-10,[7,10,22],[15,19,46],[34,30,64]],
    [-4,[13,17,40],[44,36,78],[96,58,84]],
    [0,[26,30,64],[96,68,100],[228,124,66]],
    [6,[42,64,116],[156,116,124],[255,172,92]],
    [15,[62,108,192],[124,164,216],[212,222,232]],
    [35,[76,130,218],[140,182,234],[218,234,246]]
  ];
  function skyColors(alt){
    if(alt<=SKY[0][0])return [SKY[0][1],SKY[0][2],SKY[0][3]];
    for(var i=0;i<SKY.length-1;i++){
      var a=SKY[i],b=SKY[i+1];
      if(alt<=b[0]){
        var t=(alt-a[0])/(b[0]-a[0]);
        return [mixC(a[1],b[1],t),mixC(a[2],b[2],t),mixC(a[3],b[3],t)];
      }
    }
    var L=SKY[SKY.length-1];
    return [L[1],L[2],L[3]];
  }

  var skyFlip=false;
  function updateSky(){
    if(lat===null)return;
    var d=new Date();
    var s=sunNow(d,lat,lng);
    var alt=s.sun.alt;
    dayFactor=smooth(-4,14,alt);
    var warm=clamp(1-alt/18,0,1);

    var c=skyColors(alt);
    var grad='linear-gradient(180deg,'+rgb(c[0])+' 0%,'+rgb(c[1])+' 55%,'+rgb(c[2])+' 100%)';
    var inL=skyFlip?skyA:skyB, outL=skyFlip?skyB:skyA;
    inL.style.background=grad;
    inL.style.opacity='1';outL.style.opacity='0';
    skyFlip=!skyFlip;

    var cc=mixC([9,13,30],mixC(c[2],[255,255,255],0.55),dayFactor);
    windowEl.style.setProperty('--cloudCol','rgba('+(cc[0]|0)+','+(cc[1]|0)+','+(cc[2]|0)+','+(0.5+dayFactor*0.3).toFixed(2)+')');

    var shaftCol=mixC([255,235,190],[255,176,96],warm);
    if(dayFactor>0.03){
      shaft.style.background='linear-gradient(180deg,rgba('+(shaftCol[0]|0)+','+(shaftCol[1]|0)+','+(shaftCol[2]|0)+',.30),rgba('+(shaftCol[0]|0)+','+(shaftCol[1]|0)+','+(shaftCol[2]|0)+',.10) 55%,transparent 90%)';
    }else{
      shaft.style.background='linear-gradient(180deg,rgba(150,175,255,.14),rgba(150,175,255,.05) 55%,transparent 90%)';
    }
    updateBodies();
  }

  function updateBodies(){
    if(lat===null)return;
    var d=new Date();
    var s=sunNow(d,lat,lng);
    var alt=s.sun.alt, az=s.sun.az;
    var ref=(lat>=0)?180:0;
    var dAz=az-ref; if(dAz>180)dAz-=360; if(dAz<-180)dAz+=360;
    var sx=clamp(50+(dAz/95)*48,4,96);
    var sy=clamp(70-alt*(62/90),6,86);
    sunEl.style.left=sx+'%';
    sunEl.style.top=sy+'%';
    sunEl.style.opacity=clamp((alt+6)/4,0,1).toFixed(2);
    sunEl.style.transform='translate(-50%,-50%) scale('+(1+(1-clamp(alt/20,0,1))*0.35).toFixed(2)+')';

    var mAlt=s.moon.alt,mAz=s.moon.az;
    var dAz2=mAz-ref; if(dAz2>180)dAz2-=360; if(dAz2<-180)dAz2+=360;
    var mx=clamp(50+(dAz2/95)*48,4,96);
    var my=clamp(70-mAlt*(62/90),6,86);
    moonEl.style.left=mx+'%';
    moonEl.style.top=my+'%';
    moonEl.style.opacity=(clamp((mAlt+4)/4,0,1)*(0.95-dayFactor*0.5)).toFixed(2);
  }

  function startSky(){
    updateSky();
    setInterval(updateSky,5*60*1000);
    setInterval(updateBodies,30*1000);
  }
  function useFallback(){
    if(lat!==null)return;
    lat=30;
    lng=-new Date().getTimezoneOffset()/60*15;
    startSky();
  }
  useFallback();
  if(navigator.geolocation){
    navigator.geolocation.getCurrentPosition(function(p){
      lat=p.coords.latitude;lng=p.coords.longitude;
      startSky();
    },function(){},{timeout:8000});
  }

  /* ================= curtains ================= */
  var curtainsClosed=localStorage.getItem('lr-curtains')==='1';
  var curtainMix=curtainsClosed?1:0, curTween=null;
  function paintCurtainBtn(){curtainBtn.classList.toggle('active',curtainsClosed);}
  windowEl.classList.toggle('closed',curtainsClosed);
  paintCurtainBtn();
  function setCurtains(c){
    curtainsClosed=c;
    localStorage.setItem('lr-curtains',c?'1':'0');
    windowEl.classList.toggle('closed',c);
    paintCurtainBtn();wake();
    var from=curtainMix,to=c?1:0,t0=performance.now();
    if(curTween)cancelAnimationFrame(curTween);
    function step(now){
      var t=clamp((now-t0)/2300,0,1);
      var e=t<0.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
      curtainMix=from+(to-from)*e;
      if(t<1)curTween=requestAnimationFrame(step);
    }
    curTween=requestAnimationFrame(step);
  }
  curtainBtn.addEventListener('click',function(){setCurtains(!curtainsClosed);});
  windowEl.addEventListener('click',function(){setCurtains(!curtainsClosed);});

  var lastGap=-1;
  function shaftClip(gap){
    var gr=Math.round(gap*100)/100;
    if(gr===lastGap)return;
    lastGap=gr;
    if(mq.matches){
      var cx=32.86,ht=30,cb=56,hb=36;
      shaft.style.clipPath='polygon('+(cx-ht*gr).toFixed(2)+'% 0,'+(cx+ht*gr).toFixed(2)+'% 0,'+(cb+hb*gr).toFixed(2)+'% 100%,'+(cb-hb*gr).toFixed(2)+'% 100%)';
    }else{
      var cx2=13.45,ht2=13.45,cb2=48,hb2=26;
      shaft.style.clipPath='polygon('+(cx2-ht2*gr).toFixed(2)+'% 0,'+(cx2+ht2*gr).toFixed(2)+'% 0,'+(cb2+hb2*gr).toFixed(2)+'% 100%,'+(cb2-hb2*gr).toFixed(2)+'% 100%)';
    }
  }

  /* ============================================================
     FIREPLACE
     ============================================================ */
  var doorClosed=false, fireVal=0.85, flareUntil=0, logCount=2;

  fpBody.addEventListener('click',function(){
    doorClosed=!doorClosed;
    fireplaceEl.classList.toggle('door-closed',doorClosed);
    doorClick();wake();
  });

  logPile.addEventListener('click',function(e){
    e.stopPropagation();
    var pile=logPile.getBoundingClientRect();
    var mouth=fpBody.getBoundingClientRect();
    var sx=pile.left+pile.width*0.4, sy=pile.top+pile.height*0.3;
    var el=document.createElement('span');el.className='fly-log';
    el.style.left=sx+'px';el.style.top=sy+'px';
    el.style.setProperty('--dx',(mouth.left+mouth.width*0.5-sx-17)+'px');
    el.style.setProperty('--dy',(mouth.top+mouth.height*0.8-sy-5)+'px');
    document.body.appendChild(el);
    playToss();
    el.addEventListener('animationend',function(){
      this.remove();
      if(logCount<4){
        logCount++;
        fpLogs.classList.toggle('l3',logCount>=3);
        fpLogs.classList.toggle('l4',logCount>=4);
      }
      flareUntil=Date.now()+1700;
      fireEl.classList.remove('surge');void fireEl.offsetWidth;fireEl.classList.add('surge');
      thud();crackleOnce();
      setTimeout(crackleOnce,180);
      var mx=mouth.left+mouth.width*0.5, my=mouth.top+mouth.height*0.55;
      for(var k=0;k<7;k++){
        var sp=document.createElement('span');sp.className='fspark';
        sp.style.left=mx+'px';sp.style.top=my+'px';
        sp.style.setProperty('--dx',(Math.random()*70-35)+'px');
        sp.style.setProperty('--dy',(-30-Math.random()*70)+'px');
        document.body.appendChild(sp);
        sp.addEventListener('animationend',function(){this.remove();});
      }
    });
    wake();
  });

  /* rising embers */
  setInterval(function(){
    if(Math.random()<0.55){
      if(emberbox.childElementCount>4)return;
      var em=document.createElement('i');em.className='ember';
      em.style.left=(30+Math.random()*40)+'%';
      em.style.setProperty('--ex',(Math.random()*24-12)+'px');
      em.style.animationDuration=(1.2+Math.random()*0.9)+'s';
      emberbox.appendChild(em);
      em.addEventListener('animationend',function(){this.remove();});
    }
  },650);

  /* ================= lighting (lamp + sun/moon + fire) ================= */
  var litObjs=[];
  function reg(id,fx,fy,k,base,lift){
    var el=document.getElementById(id);
    if(el)litObjs.push({el:el,fx:fx,fy:fy,k:k,base:base||1,lift:lift||0.22,lastI:-1,lastB:-1});
  }
  reg('windowEl',0.11,0.23,0.35);
  reg('frame1',0.45,0.19,0.75);
  reg('frame2',0.555,0.225,0.75);
  reg('clockEl',0.645,0.20,0.8);
  reg('plantEl',0.235,0.78,0.95);
  reg('catEl',0.42,0.86,1.0);
  reg('fireplaceEl',0.105,0.68,0.9);
  reg('timeplate',0.87,0.40,0.55,0.55,0.8);

  var lastPoolO='',lastRugO='',lastShaftO='',lastDaylightO='',lastDaypoolO='',lastNightO='',
      lastFpO='',lastFirepoolO='';
  function lightTick(){
    var on=body.classList.contains('lamp-on')?1:0;
    var open=clamp(1-curtainMix*1.12,0,1);
    shaftClip(open);

    /* fire flicker */
    if(Date.now()<flareUntil){fireVal+=(1.7-fireVal)*0.25;}
    else{fireVal+=(0.85-fireVal)*0.08+(Math.random()-0.5)*0.09;}
    fireVal=clamp(fireVal,0.55,1.7);
    var doorFactor=doorClosed?0.5:1;
    var fpO=Math.min(1,fireVal*doorFactor*0.9).toFixed(3);
    if(fpO!==lastFpO){fpGlow.style.opacity=fpO;lastFpO=fpO;}
    var fpoolO=(Math.min(1,fireVal)*doorFactor*0.85).toFixed(3);
    if(fpoolO!==lastFirepoolO){firepoolEl.style.opacity=fpoolO;lastFirepoolO=fpoolO;}

    var poolO=(on*lumVal*0.95).toFixed(3);
    if(poolO!==lastPoolO){floorpool.style.opacity=poolO;lastPoolO=poolO;}
    var rugO=(on*lumVal*0.85).toFixed(3);
    if(rugO!==lastRugO){rugLight.style.opacity=rugO;lastRugO=rugO;}

    var shaftO=((dayFactor>0.03?dayFactor*0.85:(1-dayFactor)*0.55)*(1-on*0.45)*open).toFixed(3);
    if(shaftO!==lastShaftO){shaft.style.opacity=shaftO;lastShaftO=shaftO;}
    var dlO=(dayFactor*0.17*open).toFixed(3);
    if(dlO!==lastDaylightO){daylightEl.style.opacity=dlO;lastDaylightO=dlO;}
    var dpO=(dayFactor*0.5*open*(1-on*0.3)).toFixed(3);
    if(dpO!==lastDaypoolO){daypool.style.opacity=dpO;lastDaypoolO=dpO;}
    var nO=(1-dayFactor).toFixed(3);
    if(nO!==lastNightO){nightbits.style.opacity=nO;lastNightO=nO;}

    var winX=0.10*W,winY=0.22*H;
    var firX=0.115*W,firY=0.72*H;
    for(var i=0;i<litObjs.length;i++){
      var o=litObjs[i];
      var fx=o.fx,fy=o.fy;
      if(o.el===timeplate&&mq.matches){fx=0.5;fy=0.58;}
      var ox=fx*W,oy=fy*H;

      var vx=curBulbX-ox,vy=curBulbY-oy;
      var d=Math.sqrt(vx*vx+vy*vy)||1;
      var fall=1.06-d/(H*0.95); if(fall<0)fall=0;
      var lampI=on*lumVal*fall*o.k; if(lampI>1)lampI=1;

      var dx=winX-ox,dy=winY-oy;
      var d2=Math.sqrt(dx*dx+dy*dy)||1;
      var fall2=1.15-d2/(W*0.95); if(fall2<0)fall2=0;
      var dayI=dayFactor*open*0.42*fall2*o.k; if(dayI>1)dayI=1;

      var fxv=firX-ox,fyv=firY-oy;
      var d3=Math.sqrt(fxv*fxv+fyv*fyv)||1;
      var fall3=1.12-d3/(H*0.95); if(fall3<0)fall3=0;
      var fireI=fireVal*doorFactor*fall3*o.k*0.55; if(fireI>1.4)fireI=1.4;

      var nx,ny,inten;
      if(lampI>=dayI&&lampI>=fireI){nx=vx/d;ny=vy/d;inten=lampI;}
      else if(dayI>=fireI){nx=dx/d2;ny=dy/d2;inten=dayI;}
      else{nx=fxv/d3;ny=fyv/d3;inten=fireI;}

      var br=o.base+inten*o.lift+dayFactor*open*0.10;
      if(Math.abs(inten-o.lastI)<0.03&&Math.abs(br-o.lastB)<0.02)continue;
      o.lastI=inten;o.lastB=br;
      o.el.style.filter=
        'brightness('+br.toFixed(3)+') '+
        'drop-shadow('+(nx*2).toFixed(1)+'px '+(ny*2).toFixed(1)+'px 2px rgba(255,208,150,'+(inten*0.55).toFixed(3)+')) '+
        'drop-shadow('+(nx*6).toFixed(1)+'px '+(ny*6).toFixed(1)+'px 9px rgba(255,192,122,'+(inten*0.34).toFixed(3)+')) '+
        'drop-shadow('+(nx*13).toFixed(1)+'px '+(ny*13).toFixed(1)+'px 24px rgba(255,180,110,'+(inten*0.18).toFixed(3)+'))';
    }
  }
  setInterval(lightTick,110);

  /* ================= lamp toggle ================= */
  function isOn(){return body.classList.contains('lamp-on');}
  function burst(){
    for(var k=0;k<10;k++){
      var sp=document.createElement('span');sp.className='spark';
      sp.style.setProperty('--dx',(Math.random()*140-70)+'px');
      sp.style.setProperty('--dy',(-20-Math.random()*90)+'px');
      sp.style.animationDuration=(0.6+Math.random()*0.5)+'s';
      assembly.appendChild(sp);
      sp.addEventListener('animationend',function(){this.remove();});
    }
  }
  function setLamp(on){
    if(on===isOn())return;
    body.classList.toggle('lamp-on',on);
    fixture.classList.toggle('on',on);
    impulse(0.5);
    playTick(on);
    if(on)burst();
  }
  function toggleLamp(){setLamp(!isOn());wake();}
  document.getElementById('shadeDome').addEventListener('click',toggleLamp);
  document.getElementById('bulbGlass').addEventListener('click',toggleLamp);

  var pulling=false,startY=0,maxD=0,fired=false,startT=0;
  chainHit.addEventListener('pointerdown',function(e){
    e.preventDefault();
    try{chainHit.setPointerCapture(e.pointerId);}catch(err){}
    pulling=true;startY=e.clientY;maxD=0;fired=false;startT=Date.now();
    assembly.classList.add('dragging');wake();
  });
  chainHit.addEventListener('pointermove',function(e){
    if(!pulling)return;
    var dy=e.clientY-startY; if(dy<0)dy=0; if(dy>26)dy=26;
    if(dy>maxD)maxD=dy;
    assembly.style.setProperty('--pull',dy+'px');
    if(!fired&&dy>=18){fired=true;toggleLamp();}
  });
  function endPull(){
    if(!pulling)return;
    pulling=false;
    assembly.classList.remove('dragging');
    assembly.style.setProperty('--pull','0px');
    if(!fired&&maxD<6&&(Date.now()-startT)<450)toggleLamp();
  }
  chainHit.addEventListener('pointerup',endPull);
  chainHit.addEventListener('pointercancel',endPull);
  chainHit.addEventListener('keydown',function(e){
    if(e.key==='Enter'||e.key===' '){e.preventDefault();toggleLamp();}
  });

  /* ================= the cat (silent) ================= */
  var lastPet=0;
  function spawnHearts(x,y){
    for(var k=0;k<3;k++){
      var h=document.createElement('span');h.className='heart';
      h.style.left=(x-4+Math.random()*18-9)+'px';
      h.style.top=(y-8-Math.random()*10)+'px';
      h.style.animationDelay=(k*0.12)+'s';
      document.body.appendChild(h);
      h.addEventListener('animationend',function(){this.remove();});
    }
  }
  function petCat(x,y){
    var now=Date.now();
    if(now-lastPet<900)return;
    lastPet=now;
    spawnHearts(x,y);
    catEl.classList.add('pet','excited');
    setTimeout(function(){catEl.classList.remove('pet');},1300);
    setTimeout(function(){catEl.classList.remove('excited');},2600);
    wake();
  }
  catEl.addEventListener('pointerdown',function(e){
    petCat(e.clientX,e.clientY);
  });
  catEl.addEventListener('pointermove',function(e){
    if(e.buttons)petCat(e.clientX,e.clientY);
  });
  function catAmbient(){
    setTimeout(function(){
      var r=Math.random();
      if(r<0.45){
        catEl.classList.add(Math.random()<0.5?'tilt-l':'tilt-r');
        setTimeout(function(){catEl.classList.remove('tilt-l','tilt-r');},1700);
      }else if(r<0.75){
        catEl.classList.add('twitch');
        setTimeout(function(){catEl.classList.remove('twitch');},950);
      }else{
        catEl.classList.add('excited');
        setTimeout(function(){catEl.classList.remove('excited');},2600);
      }
      catAmbient();
    },12000+Math.random()*13000);
  }
  catAmbient();

  /* ================= brown-outs & gusts ================= */
  function scheduleBrownout(){
    setTimeout(function(){
      if(isOn()){
        lumVal=0.42;root.style.setProperty('--lum','0.42');
        setTimeout(function(){
          lumVal=1;root.style.setProperty('--lum','1');
          if(Math.random()<0.4){
            setTimeout(function(){
              lumVal=0.55;root.style.setProperty('--lum','0.55');
              setTimeout(function(){lumVal=1;root.style.setProperty('--lum','1');},70);
            },120);
          }
        },75);
      }
      scheduleBrownout();
    },8000+Math.random()*10000);
  }
  scheduleBrownout();
  function scheduleGust(){
    setTimeout(function(){
      impulse(0.12+Math.random()*0.18);
      scheduleGust();
    },18000+Math.random()*17000);
  }
  scheduleGust();

  /* ================= dust ================= */
  for(var i=0;i<26;i++){
    var m=document.createElement('span');m.className='mote';
    m.style.left=(30+Math.random()*40)+'%';
    m.style.top=(8+Math.random()*88)+'%';
    var s=(1.4+Math.random()*2.6)+'px';m.style.width=s;m.style.height=s;
    m.style.animationDuration=(7+Math.random()*9)+'s';
    m.style.animationDelay=(-Math.random()*14)+'s';
    motesLayer.appendChild(m);
  }
  for(var f=0;f<6;f++){
    var fl=document.createElement('span');fl.className='mote';
    fl.style.position='absolute';
    fl.style.left=(10+Math.random()*45)+'%';
    fl.style.top=(30+Math.random()*50)+'%';
    var fs=(2.5+Math.random()*2.5)+'px';fl.style.width=fs;fl.style.height=fs;
    fl.style.filter='blur(2px)';
    fl.style.animationDuration=(16+Math.random()*12)+'s';
    fl.style.animationDelay=(-Math.random()*20)+'s';
    body.appendChild(fl);
  }

  /* ================= clocks ================= */
  var hourH=document.getElementById('hourH'),minH=document.getElementById('minH'),secH=document.getElementById('secH');
  var timeText=document.getElementById('timeText'),dateText=document.getElementById('dateText');
  function pad(n){return (n<10?'0':'')+n;}
  function tickClock(){
    var d=new Date(),h=d.getHours()%12,mn=d.getMinutes(),sc=d.getSeconds();
    hourH.style.transform='translateX(-50%) rotate('+(h*30+mn*0.5)+'deg)';
    minH.style.transform='translateX(-50%) rotate('+(mn*6+sc*0.1)+'deg)';
    secH.style.transform='translateX(-50%) rotate('+(sc*6)+'deg)';
    timeText.textContent=pad(d.getHours())+':'+pad(mn);
    dateText.textContent=d.toLocaleDateString(undefined,{weekday:'long',month:'long',day:'numeric'});
  }
  tickClock();setInterval(tickClock,1000);

  var spots=[['9vw','36%'],['13vw','26%'],['8vw','50%'],['16vw','42%']];
  var spotI=0;
  setInterval(function(){
    spotI=(spotI+1)%spots.length;
    if(mq.matches)return;
    timeplate.style.right=spots[spotI][0];
    timeplate.style.top=spots[spotI][1];
  },70000);

  /* ================= fullscreen + keep awake ================= */
  var wakeLock=null,fsActive=false;
  function paintSS(){ssBtn.classList.toggle('active',fsActive||!!wakeLock);}
  async function enableSaver(){
    try{
      var de=document.documentElement;
      if(de.requestFullscreen)await de.requestFullscreen();
      else if(de.webkitRequestFullscreen)de.webkitRequestFullscreen();
    }catch(e){}
    try{
      if(navigator.wakeLock){
        wakeLock=await navigator.wakeLock.request('screen');
        wakeLock.addEventListener('release',function(){wakeLock=null;paintSS();});
      }
    }catch(e){}
    paintSS();
  }
  function disableSaver(){
    try{if(document.fullscreenElement)document.exitFullscreen();}catch(e){}
    try{if(wakeLock)wakeLock.release();}catch(e){}
  }
  ssBtn.addEventListener('click',function(){
    wake();
    if(fsActive||wakeLock)disableSaver();else enableSaver();
  });
  document.addEventListener('fullscreenchange',function(){
    fsActive=!!document.fullscreenElement;paintSS();
  });
  document.addEventListener('visibilitychange',function(){
    if(document.visibilityState==='visible'){
      updateSky();
      if(fsActive&&navigator.wakeLock&&!wakeLock){
        navigator.wakeLock.request('screen')
          .then(function(wl){wakeLock=wl;paintSS();})
          .catch(function(){});
      }
    }
  });

  /* ================= keyboard ================= */
  addEventListener('keydown',function(e){
    if(e.key.toLowerCase()==='l'||e.code==='Space'){e.preventDefault();toggleLamp();}
    else if(e.key.toLowerCase()==='f'){ssBtn.click();}
    else if(e.key.toLowerCase()==='s'){soundBtn.click();}
    else if(e.key.toLowerCase()==='c'){curtainBtn.click();}
    wake();
  });

  /* ================= idle cursor hide ================= */
  var idleT=null;
  function wake(){
    body.classList.remove('idle');
    clearTimeout(idleT);
    idleT=setTimeout(function(){body.classList.add('idle');},3200);
  }
  addEventListener('pointermove',wake);
  addEventListener('pointerdown',wake);
  wake();

  /* ================= boot ================= */
  function hideBoot(){
    if(boot.classList.contains('done'))return;
    boot.classList.add('done');
    setTimeout(function(){boot.remove();},1100);
    setTimeout(function(){setLamp(true);},900);
  }
  setTimeout(hideBoot,2300);
  document.addEventListener('pointerdown',function(){hideBoot();},{once:true});
})();
</script>
</body>
</html>
"""


def ensure_certs():
    if os.path.exists(KEY_FILE) and os.path.exists(CRT_FILE):
        return True
    if not shutil.which("openssl"):
        return False
    try:
        subprocess.run(
            ["openssl", "req", "-x509", "-newkey", "rsa:2048",
             "-keyout", KEY_FILE, "-out", CRT_FILE,
             "-days", "365", "-nodes", "-subj", "/CN=lamp-room"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.0)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "127.0.0.1"


class Handler(BaseHTTPRequestHandler):
    server_version = "LampRoom/4.1"
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        self.send_response(200)
        data = PAGE.encode("utf-8")
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        sys.stdout.write("  · %s %s\n" % (self.address_string(), fmt % args))
        sys.stdout.flush()


def main():
    tls = ensure_certs()
    port = 8443 if tls else 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("port must be a number")
            return

    lan_ip = get_lan_ip()
    scheme = "https" if tls else "http"
    print()
    print("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("   L A M P   R O O M   4.1 — rich fire")
    print("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("   this device : %s://127.0.0.1:%d" % (scheme, port))
    print("   your WiFi   : %s://%s:%d   <- open this" % (scheme, lan_ip, port))
    print()
    if tls:
        print("   accept the browser warning once (self-signed")
        print("   cert) — needed for location, wake-lock, etc.")
    print("   Ctrl+C to stop.")
    print()

    wake_lock = shutil.which("termux-wake-lock")
    if wake_lock:
        try:
            subprocess.run([wake_lock], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    try:
        server = ThreadingHTTPServer((HOST, port), Handler)
        if tls:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(CRT_FILE, KEY_FILE)
            server.socket = ctx.wrap_socket(server.socket, server_side=True)
    except OSError as e:
        print("could not start: %s" % e)
        return

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  turning the lamp off... bye")
    finally:
        server.server_close()
        if wake_lock and shutil.which("termux-wake-unlock"):
            try:
                subprocess.run(["termux-wake-unlock"], check=False,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass


if __name__ == "__main__":
    main()
