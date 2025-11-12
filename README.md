# 🛒 Voice Command Shopping Assistant

**Voice Command Shopping Assistant** is a smart, multilingual e-commerce web application that lets users shop using **voice commands** instead of typing or clicking.  
It’s designed as a mini grocery store platform with a **voice-based shopping list manager** that provides **smart suggestions, multilingual support**, and a **persistent cart** system.

---

## 🚀 Features

- 🎤 **Voice Command Shopping** – Add, remove, or search for products using natural voice commands.  
  Examples: “Add 2 packets of milk”, “Remove bread from my cart”, “Find fruits”.
- 🌍 **Multilingual Support** – Understands English, Hindi, Telugu, Tamil, Malayalam, and Bengali.
- 🧠 **Smart NLP Engine** – Detects user intent (add, remove, search) and matches the right product dynamically.
- 💡 **Smart Suggestions** – Recommends related products or alternatives if the requested one is unavailable.
- 🛍️ **Persistent Cart System** – Cart items remain even after logout. When the same user logs back in, their previous cart is restored automatically.
- ⚡ **Real-time Interaction** – Uses the Web Speech API for instant voice recognition and FastAPI for lightning-fast backend responses.

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | React, TypeScript, Tailwind CSS |
| **Backend** | Python, FastAPI |
| **Database** | MongoDB |
| **Voice Recognition** | Web Speech API |
| **Language/NLP** | langdetect, regex-based NLP |

---

## 🧭 How It Works

1. 🎙️ User speaks a command like “Add two apples”.
2. 🧠 Browser converts speech to text and sends it to the FastAPI backend.
3. ⚙️ NLP detects intent, product, and quantity.
4. 🛒 Cart updates instantly in the frontend.
5. 💾 Cart data is saved and restored for returning users.

---

## 🔑 Login System

Users can **log in using their name**.  
If a user logs out and later logs back in with the same name,  
🛍️ **their previous cart items remain available** — ensuring a continuous shopping experience.

---

## ❤️ Developed By

**Kanni (Arepalli Umamahesh)**  
🎓 B.Tech Student | 💻 Full Stack Developer | 🤖 AI & Vision Enthusiast  
📫 **GitHub:** [@Umamahesh-1726](https://github.com/Umamahesh-1726)

⭐ *If you like this project, give it a star on GitHub!* 🌟
