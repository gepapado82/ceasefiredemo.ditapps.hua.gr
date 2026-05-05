<script>
import { data } from "autoprefixer";
import { defineComponent } from 'vue';
import CryptoJS from 'crypto-js';

function getPublicFiles() {
  // Get all files from the public directory using Vite's import.meta.glob
  const originalFiles = import.meta.glob('/public/detection/original/**/*.{png,jpg,jpeg}', { eager: true });
  const predictionFiles = import.meta.glob('/public/detection/predictions/**/*.{png,jpg,jpeg}', { eager: true });

  const images = Object.keys(originalFiles).map(key => {
    const fileName = key.split('/').pop();
    const pathWithoutPublic = key.replace('/public', '');
    return {
      src: pathWithoutPublic,
      prediction: pathWithoutPublic.replace('/original/', '/predictions/'),
      name: fileName,
      // Extract class number from path (assuming format /class_X/)
      class: parseInt(key.match(/class_(\d+)/)?.[1] || '0')
    };
  });

  return images;
}

function getDetectionFiles() {
  // Get all .txt detection files from the public directory
  const detectionFiles = import.meta.glob('/public/detection/predictions/**/*.txt', {
    eager: true,
    as: 'raw'  // This tells Vite to import the raw content
  });

  // Group detections by filename (without extension)
  const grouped = {};

  Object.keys(detectionFiles).forEach(key => {
    const fileName = key.split('/').pop();
    const baseName = fileName.replace(/\.txt$/, '');
    const pathWithoutPublic = key.replace('/public', '');
    const content = detectionFiles[key].default || detectionFiles[key];

    // Parse the content - assuming each line contains a detection
    const detections = content.split('\n')
      .filter(line => line.trim())
      .map(line => {
        const [class_id, conf, x, y, w, h] = line.split(' ').map(Number);
        return {
          class_id,
          confidence: conf,
          bbox: [x, y, w, h]
        };
      });

    grouped[baseName] = {
      src: pathWithoutPublic,
      name: fileName,
      detections
    };
  });

  // Return as an array if needed, or keep as object for lookup
  console.log("Grouped detection files:", grouped);

  return grouped;
}

function getGTFiles() {
  // Get all .txt detection files from the public directory
  const detectionFiles = import.meta.glob('/public/detection/gt/**/*.txt', {
    eager: true,
    as: 'raw'  // This tells Vite to import the raw content
  });

  // Group detections by filename (without extension)
  const grouped = {};

  Object.keys(detectionFiles).forEach(key => {
    const fileName = key.split('/').pop();
    const baseName = fileName.replace(/\.txt$/, '');
    const pathWithoutPublic = key.replace('/public', '');
    const content = detectionFiles[key].default || detectionFiles[key];

    // Parse the content - assuming each line contains a detection
    const detections = content.split('\n')
      .filter(line => line.trim())
      .map(line => {
        const [class_id, conf, x, y, w, h] = line.split(' ').map(Number);
        return {
          class_id,
          confidence: conf,
          bbox: [x, y, w, h]
        };
      });

    grouped[baseName] = {
      src: pathWithoutPublic,
      name: fileName,
      detections
    };
  });

  // Return as an array if needed, or keep as object for lookup
  console.log("Grouped detection files:", grouped);

  return grouped;
}

export default defineComponent({
  name: 'ImageLabel',
  data() {
    const salt = 'a1b2c3d4';
    const clearText = 'ceasefiredemoSRE2025';
    // precompute hash + salt
    const STORED_HASH = CryptoJS.SHA256(clearText + salt).toString();
    return {
      pwInput: '',
      error: false,
      authenticated: false,
      salt,
      STORED_HASH,
      api_data: null,
      api_labels: null,
      api_confidences: null,
      api_url: "/api/predict_vis",
      url_headers: ["Access-Control-Allow-Origin: *"],
      labels: ['Metal Pistols',
        'Threat',
        'Components',
        'Plastic Pistols',
        'Revolvers',
        'Shotguns',
        'SMGs',
        'Ammunition',
        'Rifles'
      ],
      all_filenames: null,
      staticImages: getPublicFiles(),
      staticDetections: getDetectionFiles(),
      gtDetections: getGTFiles(),
      selectedPrediction: null,
      expanded: null,
      loading: false,
      showModal: false,
      selectedFilters: [],
      showInstructionsContent: true,
    };
  },
  methods: {
    quasarUploadImage(file) {
      console.log(`Quasar received ${file.length
        } files`);
      this.sendImage(file[0]);
    },
    resetImage: function () {
      this.image = null;
      this.preview = null;
    },
    async showPrediction(predictionPath) {
      this.loading = true;
      this.showModal = true;
      await new Promise(resolve => setTimeout(resolve, 150));
      this.selectedPrediction = predictionPath;
      this.loading = false;
    },
    resetPrediction() {
      this.selectedPrediction = null;
    },
    toggleFilter(classIndex) {
      const index = this.selectedFilters.indexOf(classIndex);
      if (index === -1) {
        this.selectedFilters.push(classIndex);
      } else {
        this.selectedFilters.splice(index, 1);
      }
    },
    clearFilters() {
      this.selectedFilters = [];
    },
    checkPassword() {
      // hash the input + same salt
      const inputHash = CryptoJS.SHA256(this.pwInput + this.salt).toString();
      if (inputHash === this.STORED_HASH) {
        this.authenticated = true;
        // sessionStorage.setItem('fakeAuth', 'true');
        this.error = false;
      } else {
        this.error = true;
      }
      this.pwInput = '';
    },
    logout() {
      this.authenticated = false;
      // sessionStorage.removeItem('fakeAuth');
    }
  },
  computed: {
    exampleImages() {
      if (!this.staticImages) return [];

      let filteredImages = this.staticImages;

      // Apply filters if any are selected
      if (this.selectedFilters.length > 0) {
        filteredImages = filteredImages.filter(image =>
          this.selectedFilters.includes(image.class)
        );
      }

      return filteredImages
        .map(image => ({
          ...image,
          description: `Ground Truth Class: ${this.labels[image.class]}`
        }))
        .sort(() => Math.random() - 0.5)
        .slice(0, 200);
    },
  },
  created() {
    this.authenticated = sessionStorage.getItem('fakeAuth') === 'true';
  },
});
</script>

<template>
  <q-page class="flex flex-center">
    <q-card v-if="!authenticated" class="login-card q-pa-md">
      <q-card-section class="text-center q-pb-md">
        <div class="text-h5 text-weight-bold q-mb-sm">X-ray illicit firearms detection demo</div>
        <div class="text-h6 text-grey-8 text-weight-bold">Access Required</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit.prevent="checkPassword">
          <q-input v-model="pwInput" type="password" label="Enter password" :error="error"
            error-message="Incorrect password" autofocus outlined class="q-mb-md" />
          <div class="row justify-center">
            <q-btn label="Submit" type="submit" color="primary" unelevated rounded class="full-width" />
          </div>
        </q-form>
      </q-card-section>
    </q-card>

    <div v-else class="full-width">
      <div class="text-h3 q-pa-md text-center">X-ray illicit firearms detection demo</div>

      <div class="row justify-center q-mb-md">
        <div class="instructions-box text-body1" :class="{ 'minimized': !showInstructionsContent }">
          <div class="row items-center justify-between">
            <div class="text-h5 q-mr-sm"><b>Instructions </b></div>
            <q-btn flat round dense :icon="showInstructionsContent ? 'keyboard_arrow_down' : 'keyboard_arrow_up'"
              @click="showInstructionsContent = !showInstructionsContent" />
          </div>
          <div v-show="showInstructionsContent">
            <ul class="q-ma-none">
              <li><b>This demo</b> showcases an AI model that detects illicit firearms in X-ray baggage images.</li>
              <li><b>Browse images:</b> A grid of sample X-ray images is displayed below, showing various weapon
                types.
              </li>
              <li><b>Filter by weapon type:</b> Use the filter buttons to show only specific categories (pistols,
                rifles,
                ammunition, etc.).</li>
              <li><b>View predictions:</b> Click any image to open a detailed view with AI analysis.</li>
              <li><b>Compare results:</b> In the detailed view, switch between three modes:
                <ul>
                  <li><b>Original:</b> The raw X-ray image without annotations</li>
                  <li><b>AI Predictions:</b> Blue bounding boxes showing what the AI detected, with confidence scores
                  </li>
                  <li><b>Ground Truth:</b> Red boxes showing the actual weapon locations (expert annotations)</li>
                </ul>
              </li>
              <li><b>Detection details:</b> The right panel lists all detected items with their weapon type and
                confidence
                level.</li>
              <li><b>Model performance:</b> Compare AI predictions (blue) with ground truth (red) to evaluate
                accuracy.
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="filter-section q-mb-xl">
        <div class="text-subtitle1 q-mb-md text-grey-8 text-center">
          Filter images by weapon type
        </div>

        <div class="row justify-center">
          <div class="filter-container">
            <div class="row items-center q-gutter-sm q-pa-md">
              <q-icon name="filter_alt" size="24px" class="q-mr-md" color="primary" />
              <q-btn v-for="(label, index) in labels" :key="index" :label="label"
                :color="selectedFilters.includes(index) ? 'primary' : 'grey-4'"
                :text-color="selectedFilters.includes(index) ? 'white' : 'black'" @click="toggleFilter(index)" rounded
                class="filter-button" no-caps />
              <q-btn v-if="selectedFilters.length" label="Clear Filters" color="red-5" text-color="white"
                @click="clearFilters" rounded no-caps class="clear-button q-ml-lg" />
            </div>
          </div>
        </div>
      </div>

      <!-- Show all images -->
      <div class="row justify-center q-pa-md">
        <div class="col-12 col-md-11 col-xl-10">
          <div class="q-gutter-xs">
            <q-list class="image-grid q-mt-md">
              <div class="row justify-center q-gutter-none">
                <div v-for="(image, index) in exampleImages" :key="index"
                  class="col-xs-12 col-sm-6 col-md-4 col-lg-4 minimal-padding">
                  <q-card class="example-card cursor-pointer" @click="showPrediction(image.prediction)">
                    <q-img :src="image.src" :ratio="1" spinner-color="primary" class="image-card">
                      <!-- ...existing template slot... -->
                    </q-img>
                  </q-card>
                </div>
              </div>
            </q-list>
          </div>
        </div>
      </div>

      <!-- Show prediction modal -->
      <q-dialog v-model="showModal">
        <q-card class="modal-card">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h5 text-weight-bold q-ml-sm">Selected image</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup @click="resetPrediction" class="q-mr-sm" />
          </q-card-section>

          <q-card-section horizontal class="content-section q-pa-md">
            <!-- Left side - Image section -->
            <q-card-section class="col-9 q-pr-md">
              <div v-if="loading" class="full-height column flex-center">
                <q-spinner color="primary" size="50px" />
              </div>
              <div v-else class="full-height">
                <!-- View toggle buttons -->
                <div class="row justify-center q-mb-md">
                  <div class="view-toggle-buttons row items-center q-gutter-x-sm">
                    <q-btn icon="refresh" rounded unelevated
                      @click="selectedPrediction = selectedPrediction.replace(/\/(predictions|gt)\//, '/original/')"
                      label="Show Original" size="md" :disable="selectedPrediction.includes('/original/')"
                      :class="{ 'active': selectedPrediction.includes('/original/') }" />
                    <q-btn icon="fact_check" rounded unelevated
                      @click="selectedPrediction = selectedPrediction.replace(/\/(original|gt)\//, '/predictions/')"
                      label="Show Predictions" size="md" :disable="selectedPrediction.includes('/predictions/')"
                      :class="{ 'active': selectedPrediction.includes('/predictions/') }" color="info" />
                    <q-btn icon="visibility" rounded unelevated
                      @click="selectedPrediction = selectedPrediction.replace(/\/(original|predictions)\//, '/gt/')"
                      label="Show Ground Truth" size="md" :disable="selectedPrediction.includes('/gt/')"
                      :class="{ 'active': selectedPrediction.includes('/gt/') }" color="negative" />
                  </div>
                </div>
                <!-- Image -->
                <div class="image-container">
                  <img :src="selectedPrediction" />
                </div>
              </div>
            </q-card-section>

            <q-separator vertical />

            <!-- Right side - Detections -->
            <q-card-section class="col-3 detections-section">
              <div class="text-h6 text-weight-bold q-mb-md">Detected weapon type</div>
              <q-scroll-area style="height: calc(100% - 50px);">
                <q-list>
                  <div>
                    Ground truth annotations
                  </div>
                  <q-item
                    v-for="(detection, index) in selectedPrediction && gtDetections[selectedPrediction.split('/').pop().replace('.png', '')]?.detections || []"
                    :key="index" class="q-px-md q-py-sm">
                    <q-item-section>
                      <div class="detection-button gt">
                        <div class="id-box">ID: {{ index + 1 }}</div>
                        <div class="class-name">{{ labels[detection.class_id] || 'Unknown' }}</div>
                      </div>
                    </q-item-section>
                  </q-item> <q-separator class="q-ma-md" />

                  <div>
                    AI model annotations
                  </div>
                  <q-item
                    v-for="(detection, index) in selectedPrediction && staticDetections[selectedPrediction.split('/').pop().replace('.png', '')]?.detections || []"
                    :key="index" class="q-px-md q-py-sm">
                    <q-item-section>
                      <div class="detection-button prediction">
                        <div class="id-box">ID: {{ index + 1 }}</div>
                        <div class="class-name">{{ labels[detection.class_id] || 'Unknown' }}</div>
                        <div class="confidence">{{ Math.round(detection.confidence * 100) }}%</div>
                      </div>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-scroll-area>
            </q-card-section>
          </q-card-section>

        </q-card>
      </q-dialog>
    </div>
  </q-page>

</template>

<style scoped>
.my-card {
  width: 100%;
  max-width: 600px;
}

.selected_label {
  border: rgb(133, 22, 22);
  border-style: solid;
  background-color: rgba(133, 22, 22, 0.2);
  font-weight: bold;
}

.text-with-outline {
  color: #fff;
  text-shadow:
    0 0 6px #000,
    0 0 2px #000,
    1px 1px 2px #000,
    -1px -1px 2px #000;
  padding: 5px;
  font-weight: bold;
}

.minimal-padding {
  padding: 1.5px;
}

.full-height {
  height: 100%;
  min-height: 400px;
}

.detection-button {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  border-radius: 8px;
  padding: 8px 12px;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.detection-button.gt {
  background: rgba(255, 59, 59, 0.9);
  color: white;
}

.detection-button.prediction {
  background: rgba(0, 210, 255, 0.9);
  color: white;
}

.detection-button .id-box {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 10px;
  border-radius: 6px;
  min-width: 32px;
  text-align: center;
  font-weight: bold;
}

.detection-button .class-name {
  flex-grow: 1;
  font-weight: 500;
}

.detection-button .confidence {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 10px;
  border-radius: 6px;
  min-width: 60px;
  text-align: center;
  font-weight: 500;
}

.detection-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.detection-button.gt:hover {
  background: rgba(255, 59, 59, 1);
}

.detection-button.prediction:hover {
  background: rgba(0, 220, 255, 1);
}

.filter-container {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: inline-block;
  margin: 0 auto;
}

.text-subtitle1 {
  font-weight: 400;
  letter-spacing: 0.01em;
}

.instructions-box {
  border: 1px solid rgba(255, 59, 59, 0.3);
  border-radius: 12px;
  background: rgba(255, 59, 59, 0.05);
  padding: 16px 24px;
  color: #666;
  line-height: 1.5;
  /* Remove max-width to allow full width */
  width: auto;
  transition: all 0.1s ease;
  max-width: 800px;
  margin: 0 auto;
}

.instructions-box ul {
  padding-left: 20px;
}

.instructions-box ul ul {
  margin-top: 4px;
}

.instructions-box li {
  margin-bottom: 4px;
}

.instructions-box.minimized {
  padding: 8px 24px;
}

.filter-section {
  background: rgba(0, 0, 0, 0.02);
  padding: 24px 0;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.filter-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
}

.filter-button {
  min-width: 120px;
  transition: all 0.2s ease;
}

.filter-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.clear-button {
  box-shadow: 0 2px 4px rgba(255, 59, 59, 0.2);
}

.clear-button:hover {
  box-shadow: 0 4px 8px rgba(255, 59, 59, 0.3);
}

.image-grid {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.image-card {
  transition: all 0.2s ease;
}

.image-card:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.minimal-padding {
  padding: 2px;
}

.modal-card {
  width: 90vw;
  max-width: 1800px;
  height: 80vh;
  background: #fafafa;
}

.content-section {
  height: calc(100% - 50px);
}

.view-toggle-buttons {
  background: rgba(255, 255, 255, 0.9);
  padding: 8px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.view-toggle-buttons .q-btn {
  min-width: 150px;
  opacity: 0.7;
  transition: all 0.2s ease;
}

.view-toggle-buttons .q-btn.active {
  opacity: 1;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.image-container {
  height: calc(100% - 60px);
  background: #2d2d2d;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.image-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.detections-section {
  background: white;
  border-radius: 8px;
  height: 100%;
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

/* Make sure the page takes full height for centering */
.q-page {
  min-height: 100vh;
}

.full-width {
  width: 100%;
}
</style>
