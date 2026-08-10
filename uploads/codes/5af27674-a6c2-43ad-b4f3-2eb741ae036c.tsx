'use client'

import Image from 'next/image'
import Link from 'next/link'
import {
  Phone,
  MessageCircle,
  MapPin,
  ArrowRight,
  DoorClosed,
  ShieldCheck,
  Warehouse,
  ChefHat,
  Archive,
  Flame,
  Scissors,
  Layers,
  ClipboardCheck,
  PencilRuler,
  Wrench,
  Gem,
} from 'lucide-react'
import { Carousel, CarouselContent, CarouselItem } from '@/components/carousel'
import { categoriesData } from '@/lib/categories-data'

const PHONE = '+919675223538'
const PHONE_DISPLAY = '+91 96752 23538'
const WA_BASE = 'https://wa.me/919675223538'
const MAPS_URL = 'https://www.google.com/maps?q=28.7925119,79.0254989&z=17&hl=en'
const waLink = (msg: string) => `${WA_BASE}?text=${encodeURIComponent(msg)}`

const categoryIcons: Record<string, typeof DoorClosed> = {
  'main-gates': DoorClosed,
  railings: Layers,
  'window-grills': ShieldCheck,
  'metal-sheds': Warehouse,
  'modular-kitchen': ChefHat,
  'almirah-wardrobes': Archive,
  welding: Flame,
  'laser-cutting': Scissors,
}

const services = [
  { label: 'Gates & Doors', icon: DoorClosed },
  { label: 'Railings', icon: Layers },
  { label: 'Window Grills', icon: ShieldCheck },
  { label: 'Metal Sheds', icon: Warehouse },
  { label: 'Modular Kitchen', icon: ChefHat },
  { label: 'Steel Furniture', icon: Archive },
  { label: 'Welding', icon: Flame },
  { label: 'Laser Cutting', icon: Scissors },
]

// Sample entries — swap in real client names/localities (with their permission)
// once you're ready. Photos are real; names/areas below are placeholders.
const recentProjects = [
  { image: '/work/gallery-main-gate-01.jpg', title: 'Designer Entrance Gate', client: 'Client Name', area: 'Add Locality' },
  { image: '/work/gallery-railing-staircase-01.jpg', title: 'Modern Staircase Railing', client: 'Client Name', area: 'Add Locality' },
  { image: '/work/gallery-kitchen-02.jpg', title: 'Steel Modular Kitchen', client: 'Client Name', area: 'Add Locality' },
  { image: '/work/gallery-almirah-wardrobe-01.jpg', title: '5-Door Steel Wardrobe', client: 'Client Name', area: 'Add Locality' },
  { image: '/work/gallery-main-gate-03.jpg', title: 'Wood-Panel Steel Gate', client: 'Client Name', area: 'Add Locality' },
  { image: '/work/gallery-railing-balcony-02.jpg', title: 'Multi-Floor Balcony Railing', client: 'Client Name', area: 'Add Locality' },
]

const whyUs = [
  { title: 'Free Site Visit', desc: 'We come measure your space, no charge', icon: ClipboardCheck },
  { title: 'Free Consultation', desc: 'Discuss your idea before you commit', icon: MessageCircle },
  { title: 'Help With Design', desc: "Don't know the design? We'll suggest one", icon: PencilRuler },
  { title: 'Any Work, Any Complexity', desc: 'Simple grill to full custom fabrication', icon: Wrench },
  { title: 'On-Site Installation', desc: 'Fitted and finished at your location', icon: DoorClosed },
  { title: 'Quality SS/MS Material', desc: 'Genuine steel, no compromise on grade', icon: Gem },
]

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-background/95 backdrop-blur border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-3.5 flex items-center justify-between">
          <h1 className="font-display text-xl md:text-2xl font-bold text-[var(--primary)] tracking-wide">
            AJN METAL SOLUTIONS
          </h1>
          <div className="hidden md:flex gap-3">
            <a
              href={`tel:${PHONE}`}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[var(--primary)] text-white font-medium hover:bg-[var(--accent)] transition-colors"
            >
              <Phone size={17} />
              Call Now
            </a>
            <a
              href={waLink('Hi, I want a quote for steel work')}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[var(--whatsapp)] text-white font-medium hover:brightness-95 transition-all"
            >
              <MessageCircle size={17} />
              WhatsApp
            </a>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative h-[92vh] md:h-[85vh] min-h-[560px] text-white bg-cover bg-center bg-no-repeat" style={{ backgroundImage: 'url(/work/hero-welding-sparks.jpg)' }}>
        <div className="absolute inset-0 bg-gradient-to-t from-[#15161a] via-[#15161a]/70 to-[#15161a]/20" />
        <div className="relative h-full max-w-7xl mx-auto px-4 flex flex-col justify-end pb-28 md:pb-20">
          <p className="font-display uppercase tracking-[0.2em] text-[var(--accent)] text-sm md:text-base mb-3">
            AJN Metal Solutions
          </p>
          <h2 className="font-display text-4xl sm:text-5xl md:text-6xl font-bold leading-[1.05] mb-4 max-w-2xl">
            Iron &amp; Steel, Built to Your Design
          </h2>
          <p className="text-base md:text-lg text-white/80 mb-8 max-w-lg">
            Gates, railings, grills, modular kitchens, steel furniture, welding &amp; laser cutting — made to order, fitted at your home.
          </p>
          <div className="flex flex-wrap gap-3">
            <a
              href={`tel:${PHONE}`}
              className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-lg bg-white text-[var(--primary)] font-semibold hover:bg-white/90 transition-colors"
            >
              <Phone size={19} />
              Call Now
            </a>
            <a
              href={waLink('Hi, I want a quote for steel work')}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-lg bg-[var(--whatsapp)] text-white font-semibold hover:brightness-95 transition-all"
            >
              <MessageCircle size={19} />
              WhatsApp Quote
            </a>
            <a
              href="#work"
              className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-lg border-2 border-white/70 text-white font-semibold hover:bg-white hover:text-[var(--primary)] transition-colors"
            >
              View Our Work
              <ArrowRight size={19} />
            </a>
          </div>
        </div>
      </section>

      {/* Services strip */}
      <section className="py-8 bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-3 overflow-x-auto no-scrollbar md:grid md:grid-cols-8 md:overflow-visible pb-1">
            {services.map((s) => (
              <div
                key={s.label}
                className="flex flex-col items-center justify-center gap-2 shrink-0 w-24 md:w-auto py-4 px-2 rounded-xl bg-background border border-border text-center"
              >
                <s.icon size={22} className="text-[var(--accent)]" />
                <span className="text-xs font-medium text-foreground leading-tight">{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Categories */}
      <section id="categories" className="py-14 md:py-20 bg-background">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-10">
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-2">Our Work, By Category</h2>
            <p className="text-muted-foreground">Tap any category to see real designs and finishes</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-5">
            {Object.entries(categoriesData).map(([slug, cat]) => {
              const Icon = categoryIcons[slug] ?? DoorClosed
              return (
                <Link key={slug} href={`/category/${slug}`} className="group bracket-corners">
                  <div className="relative h-44 md:h-56 rounded-xl overflow-hidden border border-border bg-card">
                    {cat.cover ? (
                      <Image
                        src={cat.cover}
                        alt={cat.name}
                        fill
                        sizes="(max-width: 768px) 50vw, 25vw"
                        className="object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-[var(--primary)] to-[#3d434c]">
                        <Icon size={40} className="text-white/70" />
                      </div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/10 to-transparent" />
                    <div className="absolute inset-x-0 bottom-0 p-3">
                      <h3 className="text-white font-semibold text-sm md:text-base leading-tight">{cat.name}</h3>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      {/* Our Work carousel — real photos only */}
      <section id="work" className="py-14 md:py-20 bg-card border-y border-border">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-10">
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-2">Recent Work</h2>
            <p className="text-muted-foreground">Real projects, completed and installed</p>
          </div>

          <Carousel opts={{ align: 'start', loop: true }}>
            <CarouselContent className="gap-4">
              {recentProjects.map((project, idx) => (
                <CarouselItem key={idx} className="basis-[82%] sm:basis-1/2 lg:basis-1/3">
                  <div className="bg-background border border-border rounded-xl overflow-hidden">
                    <div className="relative h-56 md:h-64">
                      <Image src={project.image} alt={project.title} fill sizes="(max-width: 768px) 90vw, 33vw" className="object-cover" />
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-base text-foreground mb-1">{project.title}</h3>
                      {/* <p className="text-sm text-muted-foreground">{project.client} · {project.area}</p> */}
                    </div>
                  </div>
                </CarouselItem>
              ))}
            </CarouselContent>
          </Carousel>
        </div>
      </section>

      {/* Why choose us */}
      <section className="py-14 md:py-20 bg-dot-grid bg-background">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="font-display text-3xl md:text-4xl font-bold text-center mb-10">Why Choose AJN Metal Solutions</h2>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 md:gap-5">
            {whyUs.map((item) => (
              <div key={item.title} className="bg-card rounded-xl p-4 md:p-6 border border-border">
                <item.icon size={24} className="text-[var(--accent)] mb-3" />
                <h3 className="text-sm md:text-lg font-semibold text-foreground mb-1">{item.title}</h3>
                <p className="text-muted-foreground text-xs md:text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-14 md:py-20 bg-gradient-to-b from-[color-mix(in_oklch,var(--accent),white_88%)] to-background">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="font-display text-3xl md:text-4xl font-bold mb-4 text-foreground">Get a Quote Today</h2>
          <p className="text-muted-foreground mb-8">
            Call or WhatsApp your requirement — send a photo, a size, or just your address. We'll quote you directly.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center mb-6">
            <a
              href={`tel:${PHONE}`}
              className="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-lg bg-[var(--primary)] text-white font-semibold hover:bg-[var(--accent)] transition-colors"
            >
              <Phone size={20} />
              Call: {PHONE_DISPLAY}
            </a>
            <a
              href={waLink('Hi, I want a quote for steel work')}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-lg bg-[var(--whatsapp)] text-white font-semibold hover:brightness-95 transition-all"
            >
              <MessageCircle size={20} />
              WhatsApp Message
            </a>
          </div>
          <a
            href={MAPS_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 text-[var(--accent)] font-medium hover:underline"
          >
            <MapPin size={18} />
            Get Directions to Our Workshop
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="font-display font-semibold text-foreground mb-1">AJN METAL SOLUTIONS</p>
          <a href={`tel:${PHONE}`} className="text-muted-foreground text-sm hover:text-[var(--accent)]">
            {PHONE_DISPLAY}
          </a>
          <p className="text-muted-foreground text-xs mt-3">&copy; {new Date().getFullYear()} AJN Metal Solutions. All rights reserved.</p>
        </div>
      </footer>

      {/* Mobile sticky contact bar */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-background border-t border-border z-50 flex gap-2 p-3 shadow-[0_-4px_16px_rgba(0,0,0,0.06)]">
        <a
          href={`tel:${PHONE}`}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-[var(--primary)] text-white font-semibold text-sm"
        >
          <Phone size={16} />
          Call
        </a>
        <a
          href={waLink('Hi, I want a quote for steel work')}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-[var(--whatsapp)] text-white font-semibold text-sm"
        >
          <MessageCircle size={16} />
          WhatsApp
        </a>
      </div>
      <div className="h-[68px] md:h-0" />
    </div>
  )
}
