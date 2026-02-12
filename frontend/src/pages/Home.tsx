import { Link } from "react-router-dom";
import { Camera, Search, Leaf, Sparkles } from "lucide-react";
import { Navbar } from "@/components/Navbar";
import DigitalPetalsShader from "@/components/ui/digital-petals-shader";

export default function Home() {
  return (
    <div className="min-h-screen">
      <Navbar />
      
      {/* Hero Section with Shader Background */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        {/* WebGL Shader Background - contained to hero only */}
        <div className="absolute inset-0">
          <DigitalPetalsShader />
        </div>
        
        {/* Content - higher z-index to stay above gradient */}
        <div className="relative z-20 container mx-auto px-4 text-center">
          <div className="max-w-3xl mx-auto space-y-8 bg-background/70 backdrop-blur-sm rounded-3xl p-8 md:p-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full text-primary text-sm font-medium animate-fade-in">
              <Sparkles className="w-4 h-4" />
              AI-Powered Flower Identification
            </div>
            
            <h1 className="text-5xl md:text-7xl font-serif font-bold text-foreground leading-tight animate-slide-up">
              Discover the
              <span className="block text-botanical-gradient">Beauty of Flowers</span>
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground max-w-xl mx-auto animate-slide-up" style={{ animationDelay: "0.1s" }}>
              Snap a photo and instantly identify any flower. Learn about care tips, bloom seasons, and more.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up" style={{ animationDelay: "0.2s" }}>
              <Link
                to="/identify"
                className="btn-botanical inline-flex items-center gap-2 text-lg"
              >
                <Camera className="w-5 h-5" />
                Identify a Flower
              </Link>
              <Link
                to="/search"
                className="btn-botanical-outline inline-flex items-center gap-2 text-lg"
              >
                <Search className="w-5 h-5" />
                Browse Species
              </Link>
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-24 left-1/2 -translate-x-1/2 animate-float z-20">
          <div className="w-6 h-10 border-2 border-foreground/30 rounded-full flex items-start justify-center p-2">
            <div className="w-1 h-2 bg-foreground/50 rounded-full animate-pulse-soft" />
          </div>
        </div>

        {/* Gradient fade to cream - lighter and positioned above features subtitle */}
        <div 
          className="absolute bottom-0 left-0 right-0 h-64 pointer-events-none z-10"
          style={{ 
            background: 'linear-gradient(to bottom, transparent 0%, rgba(245, 241, 232, 0.4) 40%, rgba(245, 241, 232, 0.8) 70%, #F5F1E8 100%)' 
          }}
        />
      </section>

      {/* Features Section - Solid Cream Background */}
      <section 
        className="py-24 pt-32" 
        style={{ 
          background: 'linear-gradient(to bottom, transparent 0%, rgba(245, 241, 232, 0.3) 20%, rgba(245, 241, 232, 0.7) 40%, #F5F1E8 60%, #F5F1E8 100%)' 
        }}
      >
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-serif font-bold text-foreground mb-4">
              How It Works
            </h2>
            <p className="text-muted-foreground max-w-lg mx-auto">
              Identifying flowers has never been easier. Just three simple steps.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              {
                icon: Camera,
                title: "Snap a Photo",
                description: "Take a picture of any flower you want to identify",
              },
              {
                icon: Sparkles,
                title: "AI Analysis",
                description: "Our AI instantly analyzes the image and identifies the species",
              },
              {
                icon: Leaf,
                title: "Learn & Grow",
                description: "Get detailed information about care, seasons, and more",
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="text-center p-8 rounded-2xl bg-white shadow-lg hover:shadow-xl transition-all duration-300"
              >
                <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-primary/10 flex items-center justify-center">
                  <feature.icon className="w-8 h-8 text-primary" />
                </div>
                <h3 className="font-serif text-xl font-semibold text-foreground mb-3">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section - Solid Botanical Green Background */}
      <section className="py-24" style={{ backgroundColor: '#2D5016' }}>
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-serif font-bold text-white mb-6">
            Ready to Explore?
          </h2>
          <p className="text-white/80 mb-8 max-w-lg mx-auto">
            Start identifying flowers today and build your botanical knowledge.
          </p>
          <Link
            to="/identify"
            className="inline-flex items-center gap-2 text-lg px-8 py-4 rounded-full font-medium transition-all duration-300 hover:scale-105"
            style={{ backgroundColor: '#E8B4B8', color: '#2D5016' }}
          >
            <Camera className="w-5 h-5" />
            Get Started
          </Link>
        </div>
      </section>

      {/* Footer - Solid Sage Green Background */}
      <footer className="py-8" style={{ backgroundColor: '#8FA888' }}>
        <div className="container mx-auto px-4 text-center text-sm text-white">
          <p>© 2024 Calyx. Built with love for flower enthusiasts.</p>
        </div>
      </footer>
    </div>
  );
}