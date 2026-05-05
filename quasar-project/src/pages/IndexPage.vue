<template>
  <div class="index-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="logo-container">
          <div class="logos-row">
            <q-img width="600px" src="FullLogo.png" class="logo main-logo" />
          </div>

          <div class="logos-row">
            <q-img width="450px" src="HUA-Logo-Blue-RGB.png" class="logo partner-logo" />
            <q-img width="150px" src="hua_cvg_logo.png" class="logo partner-logo" />
          </div>
        </div>

        <div class="hero-text">
          <h1 class="hero-title">Ceasefire EU Project</h1>
          <h2 class="hero-subtitle">Visit the <a href="https://ceasefire-project.eu/">project's official website</a> for
            more information.</h2>
        </div>
      </div>
    </div>

    <!-- Description Section -->
    <div class="description-section">
      <div class="container">
        <q-card class="description-card" flat>
          <q-card-section class="text-center">
            <p class="description-text">
              Firearms trafficking holds a prominent position at the forefront of organized crime activities in
              Europe. CEASEFIRE develops innovative, holistic, multi-disciplinary AI tools to aid EU Law
              Enforcement Agencies in detecting, analyzing and tracking cross-border illicit firearms trafficking.
            </p>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Demo Cards Section -->
    <div class="demos-section">
      <div class="container">
        <div class="demo-cards">
          <q-card class="demo-card" flat>
            <div class="card-icon">
              <q-icon name="search" size="48px" color="primary" />
            </div>
            <q-card-section class="card-content">
              <h3 class="card-title">X-ray Firearms Detection</h3>
              <p class="card-description">
                AI-powered object detection for identifying firearms and weapons in X-ray images
              </p>
            </q-card-section>
            <q-card-actions class="card-actions">
              <q-btn color="primary" unelevated rounded to="/object-detection" class="demo-button" no-caps>
                Explore Demo
                <q-icon name="arrow_forward" class="q-ml-sm" />
              </q-btn>
            </q-card-actions>
          </q-card>

          <q-card class="demo-card" flat>
            <div class="card-icon">
              <q-icon name="category" size="48px" color="secondary" />
            </div>
            <q-card-section class="card-content">
              <h3 class="card-title">Web Image Classification</h3>
              <p class="card-description">
                Advanced classification system for categorizing illicit items and contraband
              </p>
            </q-card-section>
            <q-card-actions class="card-actions">
              <q-btn color="secondary" unelevated rounded to="/image-classification" class="demo-button" no-caps>
                Explore Demo
                <q-icon name="arrow_forward" class="q-ml-sm" />
              </q-btn>
            </q-card-actions>
          </q-card>
        </div>
      </div>
    </div>

    <!-- EU Funding Acknowledgment Section -->
    <div class="funding-section">
      <div class="container">
        <div class="funding-content">
          <q-img width="80px" src="eu_logo.png" class="eu-logo" />
          <div class="funding-text">
            This project has received funding from the European Union's Horizon Europe research and innovation programme
            under grant agreement No 101073876
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.index-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.hero-section {
  padding: 24px 1px;
  text-align: center;
  /* background: linear-gradient(135deg, #898989 0%, #bcbcbc 100%); */
  color: white;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.logo-container {
  margin-bottom: 40px;
}

.logos-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.main-logo {
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.partner-logo {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  opacity: 0.9;
  transition: all 0.3s ease;
}

.partner-logo:hover {
  opacity: 1;
  transform: translateY(-2px);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .logos-row {
    gap: 30px;
  }

  .main-logo {
    width: 300px !important;
  }

  .partner-logo:first-of-type {
    width: 200px !important;
  }

  .partner-logo:last-child {
    width: 120px !important;
  }
}

@media (max-width: 768px) {
  .logos-row {
    gap: 20px;
    flex-direction: column;
  }

  .main-logo {
    width: 280px !important;
  }

  .partner-logo:first-of-type {
    width: 180px !important;
  }

  .partner-logo:last-child {
    width: 110px !important;
  }
}

@media (max-width: 480px) {
  .logos-row {
    gap: 16px;
  }

  .main-logo {
    width: 250px !important;
  }

  .partner-logo:first-of-type {
    width: 150px !important;
  }

  .partner-logo:last-child {
    width: 90px !important;
  }
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  color: black;
  margin: 0 0 8px 0;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: rgba(0, 0, 0, 0.9);
  margin: 0;
  font-weight: 300;
}

.description-section {
  padding: 60px 24px;
  background: white;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.description-card {
  background: #f8f9fa;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.description-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #555;
  margin: 0;
  max-width: 800px;
  margin: 0 auto;
}

.demos-section {
  padding: 80px 24px;
  background: linear-gradient(135deg, #f1f3f4 0%, #e8eaf6 100%);
}

.demo-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 40px;
  max-width: 1000px;
  margin: 0 auto;
}

.demo-card {
  background: white;
  border-radius: 20px;
  padding: 40px 32px;
  text-align: center;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.demo-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.demo-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--q-primary), var(--q-secondary));
}

.card-icon {
  margin-bottom: 24px;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
}

.card-description {
  font-size: 1rem;
  line-height: 1.5;
  color: #666;
  margin: 0;
}

.card-actions {
  padding: 24px 0 0 0;
  justify-content: center;
}

.demo-button {
  padding: 12px 32px;
  font-size: 1rem;
  font-weight: 500;
  min-width: 200px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
}

.demo-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .demo-cards {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .demo-card {
    padding: 32px 24px;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 40px 16px;
  }

  .logo {
    width: 300px !important;
  }

  .hero-title {
    font-size: 1.5rem;
  }
}

.funding-section {
  padding: 40px 24px;
  background: #f8f9fa;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.funding-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  max-width: 800px;
  margin: 0 auto;
  flex-wrap: wrap;
}

.eu-logo {
  flex-shrink: 0;
}

.funding-text {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
  text-align: center;
  max-width: 600px;
}

/* Responsive Design for funding section */
@media (max-width: 768px) {
  .funding-content {
    flex-direction: column;
    gap: 16px;
  }

  .funding-text {
    font-size: 0.8rem;
  }

  .eu-logo {
    width: 60px !important;
  }
}
</style>
