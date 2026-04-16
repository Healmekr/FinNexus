import { Routes, Route } from "react-router-dom";
import { Swiper, SwiperSlide } from "swiper/react";
import { Autoplay, EffectCreative } from "swiper/modules";
import "swiper/css";
import "swiper/css/effect-creative";
import Navbar from "./components/Navbar";
import Login from "./components/Login";
import Signup from "./components/Signup";
import FeaturesAndHowItWorks from "./components/FeaturesAndHowItWorks";
import Footer from "./components/Footer";
import Contact from "./components/Contact";
import Dashboard from "./components/Dashboard";
import Insights from "./components/Insights";
import PrivateRoute from "./components/PrivateRoute";
import heroBg from "./images/HeroSection.png";

function Layout() {
  const features = [
    "AI-Powered Insights – Real-time analytics that adapt to your financial habits.",
    "Instant Loan Approval – Get decisions in seconds, not days — no paperwork.",
    "Banking, Reinvented – Experience the future of finance, today.",
    "Personalized Recommendations – Tailored advice to grow your wealth.",
  ];

  return (
    <div>
      <div style={{ position: "sticky", top: 0, zIndex: 1000 }}>
        <Navbar />
      </div>

      <div 
        style={{
          backgroundImage: `url(${heroBg})`,
          backgroundSize: "cover",
          backgroundPosition: "center 30%",
          backgroundRepeat: "no-repeat",
          minHeight: "100vh",
          backgroundColor: "#3a5471",
          display: "flex",
          flexDirection: "column"
        }}
      >
        <div className="hero-content">
          <div className="hero-title-group">
            <span className="hero-welcome">Welcome to</span>
            <h1 className="hero-brand">FinNexus</h1>
          </div>
          <div className="swiper-fixed">
            <Swiper
              modules={[Autoplay, EffectCreative]}
              effect="creative"
              creativeEffect={{
                prev: { shadow: false, translate: ["-120%", 0, -1] },
                next: { shadow: false, translate: ["120%", 0, -1] },
              }}
              autoplay={{ delay: 3000, disableOnInteraction: false }}
              loop={true}
              speed={800}
              className="hero-swiper"
            >
              {features.map((feature, idx) => (
                <SwiperSlide key={idx}>
                  <p className="hero-subtitle">{feature}</p>
                </SwiperSlide>
              ))}
            </Swiper>
          </div>
          <a href="/signup" className="hero-cta">Get Started →</a>
        </div>
      </div>

      <div style={{ backgroundColor: "#3a5471" }}>
        {/* Replaced CardSection and HowItWorks with the combined component */}
        <FeaturesAndHowItWorks />
        <Footer />
      </div>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/contact" element={<Contact />} />
      <Route path="/dashboard" element={
        <PrivateRoute>
          <Dashboard />
        </PrivateRoute>
      } />
      <Route path="/insights" element={
        <PrivateRoute>
          <Insights />
        </PrivateRoute>
      } />
      <Route path="/*" element={<Layout />} />
    </Routes>
  );
}

export default App;