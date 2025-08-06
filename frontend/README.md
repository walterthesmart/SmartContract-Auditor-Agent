# HederaAuditAI Frontend

A modern, responsive Next.js frontend for the HederaAuditAI smart contract security auditor.

## 🚀 Features

- **Modern Tech Stack**: Next.js 14, TypeScript, Tailwind CSS
- **Code Editor**: Monaco Editor with syntax highlighting for Solidity/Vyper
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Real-time Updates**: Live audit results and progress tracking
- **File Upload**: Drag & drop contract file upload
- **Report Generation**: PDF audit report generation and download
- **NFT Certificates**: Display and manage audit NFT certificates
- **API Integration**: Full integration with HederaAuditAI backend
- **Type Safety**: Comprehensive TypeScript types and interfaces
- **Code Quality**: ESLint, Prettier, and strict TypeScript configuration

## 🛠️ Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Code Editor**: Monaco Editor
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast
- **File Upload**: React Dropzone
- **Animations**: Framer Motion
- **Linting**: ESLint + Prettier

## 📦 Installation

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.local.example .env.local
   ```
   
   Edit `.env.local` with your configuration:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_HEDERA_NETWORK=testnet
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

5. **Open in browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router
│   │   ├── globals.css      # Global styles
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Home page
│   ├── components/          # React components
│   │   ├── audit/           # Audit-related components
│   │   ├── editor/          # Code editor components
│   │   ├── layout/          # Layout components
│   │   ├── nft/             # NFT certificate components
│   │   ├── report/          # Report generation components
│   │   ├── tutorial/        # Tutorial components
│   │   └── ui/              # Reusable UI components
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility functions
│   ├── services/            # API services
│   └── types/               # TypeScript type definitions
├── public/                  # Static assets
├── .eslintrc.json          # ESLint configuration
├── .prettierrc             # Prettier configuration
├── next.config.js          # Next.js configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── tsconfig.json           # TypeScript configuration
```

## 🎨 Components

### Core Components

- **CodeEditor**: Monaco-based code editor with syntax highlighting
- **AuditDashboard**: Displays audit results, scores, and vulnerability summary
- **VulnerabilityList**: Interactive list of security vulnerabilities
- **ReportPreview**: PDF report generation and download
- **NFTCertificate**: NFT audit certificate display and management
- **TutorialSection**: Interactive tutorial and learning resources

### UI Components

- **Button**: Customizable button with variants and loading states
- **Card**: Reusable card component with header and actions
- **Badge**: Severity badges for vulnerabilities
- **ProgressBar**: Animated progress indicator
- **AlertContainer**: Toast notification system

## 🔧 Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues
npm run type-check   # TypeScript type checking
npm run format       # Format code with Prettier
npm run format:check # Check code formatting
```

## 🌐 API Integration

The frontend integrates with the HederaAuditAI backend API:

- **POST /analyze**: Submit contracts for security analysis
- **POST /generate-report**: Generate PDF audit reports
- **POST /upload-contract**: Upload contract files
- **GET /moonscape/status**: Get MoonScape integration status
- **GET /health**: Backend health check

## 📱 Responsive Design

The application is fully responsive with:

- **Mobile-first approach**: Optimized for mobile devices
- **Breakpoint system**: Tailored layouts for different screen sizes
- **Touch-friendly**: Optimized for touch interactions
- **Accessible**: WCAG compliant with proper ARIA labels

## 🎯 Key Features

### Smart Contract Editor
- Monaco Editor with Solidity/Vyper syntax highlighting
- File upload via drag & drop
- Real-time code editing with line numbers
- Vulnerability markers and annotations

### Audit Dashboard
- Real-time audit progress tracking
- Comprehensive vulnerability analysis
- Security score calculation
- Interactive vulnerability details

### Report Generation
- Professional PDF audit reports
- Downloadable and shareable
- Comprehensive security analysis
- Recommendations and best practices

### NFT Certificates
- Automated NFT minting for passed audits
- Hedera network integration
- Certificate verification
- Hashscan integration for viewing

## 🔒 Security

- **Type Safety**: Comprehensive TypeScript coverage
- **Input Validation**: Client-side validation for all inputs
- **Secure API Calls**: Proper error handling and timeout management
- **XSS Protection**: Sanitized user inputs and outputs

## 🚀 Deployment

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Start production server**:
   ```bash
   npm run start
   ```

3. **Deploy to Vercel** (recommended):
   ```bash
   npx vercel
   ```

## 🤝 Contributing

1. Follow the existing code style and conventions
2. Run linting and type checking before committing
3. Write meaningful commit messages
4. Test your changes thoroughly

## 📄 License

This project is licensed under the ISC License.
