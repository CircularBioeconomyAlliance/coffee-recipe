# CBA Indicator Selection - Frontend

Modern, professional web application for CBA Monitoring & Evaluation indicator selection.

## Tech Stack

- **Next.js 15** - React framework with App Router
- **React 19** - Latest React with improved performance
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icons

## Design System

### Colors
- **Navy**: `#031f35` (Primary background)
- **Gold**: `#FBAD17` (Accent/CTA)
- **Navy Light**: `#0a2a42` (Cards)
- **Navy Dark**: `#011628` (Header)

### Features
- Responsive design
- Smooth animations
- Card-based layout with glow effects
- Gradient text effects
- Professional typography

## Development

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
cba-frontend/
├── app/
│   ├── layout.tsx       # Root layout
│   ├── page.tsx         # Landing page
│   ├── chat/            # Chat interface
│   ├── upload/          # File upload
│   ├── results/         # Indicator cards
│   ├── compare/         # Comparison view
│   └── globals.css      # Global styles
├── lib/
│   └── api.ts           # API client
└── public/              # Static assets
```

## Features

- Landing page with dual entry points (Chat / Upload)
- Chat interface with live project profile sidebar
- PDF upload with AI extraction
- Indicator cards with filtering
- Side-by-side comparison view
- Real-time backend integration via AWS Lambda + AgentCore
