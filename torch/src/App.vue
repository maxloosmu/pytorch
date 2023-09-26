<template>
  <div class="container is-fluid">
    <section class="section">
      <div class="columns is-desktop">
        <div class="column is-12">
          <div v-for="folder in folders" :key="folder.name" class="control">
            <label class="checkbox">
              <input
                type="checkbox"
                name="folder"
                :value="folder.name"
                v-model="folder.checked"
                @change="updateLowerLeft(folder)"
              />
              {{ folder.name }}
            </label>
          </div>
        </div>
      </div>
    </section>
    <div class="columns is-desktop">
      <div class="lower-left-container column is-3">
        <section class="section">
          <div class="button-row is-flex is-justify-content-flex-end">
            <button class="button is-small mr-2" @click="loadHTMLContents">Load Files</button>
            <button class="button is-small mr-2" @click="compareFiles">Compare</button>
            <button class="button is-small" @click="startSlideshow">Start SlideShow</button>
            <button class="button is-small" @click="stopSlideshow">Stop SlideShow</button>
          </div>
          <ul id="selectedFolders" style="list-style-type: none;">
            <li v-for="folder in selectedFolders" :key="folder.name">
              <h3>{{ folder.name }}</h3>
              <ul id="filesInFolder" style="list-style-type: none;">
                <li v-for="file in folder.files" :key="file.name" class="control">
                  <label class="checkbox-label">
                    <input
                      type="checkbox"
                      name="file"
                      :value="file.name"
                      v-model="file.checked"
                      @change="updateFileSelection(file)"
                      :disabled="file.disabled || (!file.checked && selectedFiles.length >= 3)"
                    />
                    {{ file.name }}
                  </label>
                </li>
              </ul>
            </li>
          </ul>
        </section>
      </div>
      <transition-group :name="transitionName" tag="div" class="transition-container" :class="{ 'slideshow': isSlideshowActive, 'columns': !isSlideshowActive }">
        <div
          v-for="(file, index) in selectedFiles"
          :key="file.name"
          class="slide"
          v-show="isSlideVisible(index)"
          :class="{ 'html-container': true, 'column': !isSlideshowActive, 'is-3': !isSlideshowActive, 'active': isSlideshowActive && currentSlideIndex === index, 'slide': isSlideshowActive && currentSlideIndex !== index }"
          :style="slideStyles(index)"
        >
          <section class="section">
            <h4>{{ file.name }}</h4>
            <div v-html="lowerRightData.htmlContents[index]" class="content-area"></div>
          </section>
        </div>
      </transition-group>
    </div>
  </div>
  <div id="hiddenDiv" v-show="isHiddenDivVisible">
    <div id="closeButtonContainer" class="is-flex is-justify-content-flex-end">
      <button id="closeButton" class="button is-small" @click="closeHiddenDiv">Close
      </button>
    </div>
    <div class="columns">
      <div class="column">
        <div id="showFile1" v-html="highlightedHtml1">
        </div>
      </div>
      <div class="column">
        <div id="showFile2" v-html="highlightedHtml2">
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const folders = ref([]);
    const selectedFolders = ref([]);
    const selectedFiles = ref([]);
    const lowerRightData = ref({ htmlContents: [] });
    const isSlideshowActive = ref(false);
    const currentSlideIndex = ref(0);
    const transitionName = ref('slide-left');
    const isHiddenDivVisible = ref(false);
    const highlightedHtml1 = ref('');
    const highlightedHtml2 = ref('');
    const isComparing = ref(false);  // Add this variable to track if a comparison is in progress

    async function fetchFolders() {
      try {
        const response = await axios.get('http://localhost:3000/api/test');
        folders.value = response.data.folders.map(folder => ({
          ...folder,
          checked: false,
          files: folder.files
            .filter(file => file.name.endsWith('.html'))
            .map(file => ({ ...file, checked: false }))
        }));
      } catch (error) {
        console.error('Error fetching folders:', error);
      }
    }

    function updateLowerLeft(folder) {
      if (folder.checked) {
        if (selectedFolders.value.length < 3) {
          selectedFolders.value.push(folder);
        } else {
          folder.checked = false;
          alert('You can select a maximum of 3 folders');
        }
      } else {
        selectedFolders.value = selectedFolders.value.filter(f => f !== folder);
      }
    }

    function updateFileSelection(file) {
      if (file.checked) {
        if (selectedFiles.value.length >= 3) {
          file.checked = false;
          return;
        }
        selectedFiles.value.push(file);
      } else {
        selectedFiles.value = selectedFiles.value.filter(f => f !== file);
      }
    }

    async function loadHTMLContents() {
      lowerRightData.value.htmlContents = [];
      for (let i = 0; i < selectedFiles.value.length; i++) {
        const file = selectedFiles.value[i];
        try {
          const response = await axios.get(file.url);
          lowerRightData.value.htmlContents.push(response.data);
        } catch (error) {
          console.error('Error fetching HTML content:', error);
        }
      }
    }

    async function compareFiles() {
      // Verify if two files are selected
      if (selectedFiles.value.length !== 2) {
        const alertMessage = selectedFiles.value.length === 1
          ? '2 files are needed for Compare'
          : 'Only 2 files are needed for Compare';
        alert(alertMessage);
        return;  // end function if not exactly 2 files are selected
      }

      isComparing.value = true;  // Set isComparing to true when the comparison starts

      try {
        // Fetch HTML content of both files
        const [htmlContent1, htmlContent2] = await Promise.all(
          selectedFiles.value.map((file) => axios.get(file.url))
        );

        // console.log('htmlContent1:', htmlContent1.data);
        // console.log('htmlContent2:', htmlContent2.data);
        // Send the HTML content to your Flask server for comparison
        const response = await axios.post('http://localhost:3000/api/compare', {
          html1: htmlContent1.data,
          html2: htmlContent2.data,
        });

        // The highlighted HTML contents are now in response.data.highlightedHtml1 and response.data.highlightedHtml2.
        // You can now update your Vue.js state with these highlighted HTML contents.
        highlightedHtml1.value = response.data.highlightedHtml1;
        highlightedHtml2.value = response.data.highlightedHtml2;
        // console.log('highlightedHtml1:', highlightedHtml1.value);
        // console.log('highlightedHtml2:', highlightedHtml2.value);
        isHiddenDivVisible.value = true;

      } catch (error) {
        console.error('Error comparing files:', error);
      } finally {
        isComparing.value = false;  // Reset isComparing to false when the comparison ends (even if it ends with an error)
      }
    }

    function beforeUnload(e) {
      if (isComparing.value) {
        e.returnValue = 'A file comparison is in progress. Are you sure you want to leave?';
      }
    }

    function closeHiddenDiv() {
      isHiddenDivVisible.value = false;
    }

    function startSlideshow() {
      isSlideshowActive.value = true;
      currentSlideIndex.value = 0;
    }

    function stopSlideshow() {
      isSlideshowActive.value = false;
      currentSlideIndex.value = 0;
    }

    const isSlideVisible = computed(() => {
      return (index) => {
        return true;
      };
    });

    const slideStyles = computed(() => {
      return (index) => {
        if (isSlideshowActive.value) {
          if (currentSlideIndex.value === index) {
            return { opacity: 1, width: '50vw' };
          } else {
            return { opacity: 0.1, width: '10vw' };
          }
        } else {
          return { opacity: 1, width: '24vw' };
        }
      };
    });

    function handleKeyDown(event) {
      if (isSlideshowActive.value) {
        if (event.key === "ArrowRight" && currentSlideIndex.value < selectedFiles.value.length - 1) {
          transitionName.value = 'slide-right';
          currentSlideIndex.value++;
        } else if (event.key === "ArrowLeft" && currentSlideIndex.value > 0) {
          transitionName.value = 'slide-left';
          currentSlideIndex.value--;
        }
      }
    }

    onMounted(() => {
      fetchFolders();
      window.addEventListener('keydown', handleKeyDown);
      window.addEventListener('beforeunload', beforeUnload);
    });

    onUnmounted(() => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('beforeunload', beforeUnload);
    });

    return {
      folders,
      selectedFolders,
      updateLowerLeft,
      updateFileSelection,
      selectedFiles,
      lowerRightData,
      loadHTMLContents,
      isSlideshowActive,
      currentSlideIndex,
      startSlideshow,
      stopSlideshow,
      isSlideVisible,
      handleKeyDown,
      transitionName,
      slideStyles,
      compareFiles,
      isHiddenDivVisible,
      closeHiddenDiv,
      highlightedHtml1,
      highlightedHtml2,
      beforeUnload,
    };
  },
};
</script>

<style scoped>
.container.is-fluid {
  max-width: 100%;
  padding-left: 20px;
  padding-right: 0;
}

#filesInFolder {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

#filesInFolder > li {
  margin-bottom: 5px;
}

.content-area {
  width: 100%;
  height: 100%;
  overflow: auto;
}

.lower-left-container {
  width: 24vw;
  height: 74vh;
  overflow: auto;
}

.button-row {
  display: flex;
  flex-wrap: wrap;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
}

.checkbox-label input[type="checkbox"] {
  margin-right: 10px;
  margin-top: 8px;
}

.slideshow {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: unsafe;
  position: relative;
  height: 74vh;
  width: 75vw;
  overflow: hidden;
}

.transition-container {
  display: flex;
  overflow: hidden;
  width: 75vw;
}

.slide {
  width: 24vw;
  flex-shrink: 0;
  transition: transform 2s, opacity 2s, width 2s;
}

.html-container {
  /* width: 14vw; */
  height: 74vh;
  overflow: auto;
}

.slideshow .html-container.slide {
  display: block;
  width: 10vw;
}  

.slideshow .html-container.active {
  display: block;
  width: 50vw;
}

/* New CSS rules for the slide transition effect */
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 2s ease;
}

.slide-left-enter,
.slide-right-leave-to {
  transform: translateX(100%);
}

.slide-right-enter,
.slide-left-leave-to {
  transform: translateX(-100%);
}

.slide-left-leave-to,
.slide-right-enter,
.slide-left-enter,
.slide-right-leave-to {
  opacity: 0;
}

#hiddenDiv {
  z-index: 9;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* OPTIONAL: Move div to the center */
  background-color: white; /* Or any color you want */
  width: 50%; /* Or any size you want */
  height: 50%; /* Or any size you want */
  border: 1px solid blue; 
  overflow: auto; /* Add scroll if content is larger than div */
}

#closeButtonContainer {
  text-align: right; /* Align the button to the right */
  margin-top: 10px; /* Move the button slightly to the top */
  margin-right: 30px;
  margin-bottom: 10px; /* Add some space between the button and the content */
}
</style>
