<template>
  <div class="card-church overflow-hidden">
    <!-- 헤더 -->
    <div class="px-6 py-4 border-b" style="background-color: var(--church-navy); border-color: var(--church-navy-dark);">
      <div class="flex items-center">
        <div class="w-10 h-10 rounded-full flex items-center justify-center mr-4" style="background-color: rgba(255,255,255,0.15);">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-semibold text-white">이번 주 공과</h2>
          <p v-if="store.selectedWeek" class="text-sm" style="color: rgba(255,255,255,0.7);">
            {{ store.selectedWeek.week_range }}
          </p>
        </div>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="!store.lessonData" class="p-6">
      <div class="animate-pulse-slow space-y-4">
        <div class="h-5 rounded w-3/4" style="background-color: var(--church-light-gray);"></div>
        <div class="h-4 rounded w-full" style="background-color: var(--church-light-gray);"></div>
        <div class="h-4 rounded w-5/6" style="background-color: var(--church-light-gray);"></div>
      </div>
    </div>

    <!-- 공과 내용 -->
    <div v-else class="p-6">
      <!-- 주차 및 교재 정보 -->
      <div v-if="store.lessonData.week_info" class="mb-5 p-4 rounded-lg" style="background-color: var(--church-cream);">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="flex items-center">
            <svg class="w-4 h-4 mr-2" style="color: var(--church-gold);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="text-sm" style="color: var(--church-gray);">
              <strong style="color: var(--church-navy);">주차:</strong> {{ store.lessonData.week_info.week_range }}
            </span>
          </div>
          <div class="flex items-center">
            <svg class="w-4 h-4 mr-2" style="color: var(--church-gold);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <span class="text-sm" style="color: var(--church-gray);">
              <strong style="color: var(--church-navy);">교재:</strong> {{ store.lessonData.week_info.title_keywords }}
            </span>
          </div>
        </div>
      </div>

      <!-- 제목 -->
      <h3 class="text-lg font-semibold mb-4 pb-4 border-b" style="color: var(--church-navy); border-color: var(--church-light-gray);">
        {{ store.lessonData.title }}
      </h3>

      <!-- 내용 (펼치기/접기) -->
      <div class="mb-5">
        <button
          @click="isContentExpanded = !isContentExpanded"
          class="w-full flex items-center justify-between px-4 py-3 rounded-lg transition border"
          :style="{ 
            backgroundColor: isContentExpanded ? 'var(--church-cream)' : 'white',
            borderColor: 'var(--church-light-gray)'
          }"
        >
          <span class="flex items-center text-sm" style="color: var(--church-navy);">
            <svg class="w-4 h-4 mr-2" style="color: var(--church-gold);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            공과 원문 내용 보기
          </span>
          <svg 
            :class="['w-4 h-4 transition-transform', isContentExpanded ? 'rotate-180' : '']"
            style="color: var(--church-gray);"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        <transition name="slide">
          <div 
            v-show="isContentExpanded"
            class="mt-3 p-4 rounded-lg max-h-80 overflow-y-auto border"
            style="background-color: var(--church-cream); border-color: var(--church-light-gray);"
          >
            <div class="prose prose-sm max-w-none whitespace-pre-wrap text-sm leading-relaxed" style="color: var(--church-gray);">
              {{ store.lessonData.content }}
            </div>
          </div>
        </transition>
      </div>

      <!-- 원본 링크 -->
      <a 
        :href="store.lessonData.url" 
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex items-center text-sm transition"
        style="color: var(--church-navy);"
        @mouseenter="$event.target.style.color = 'var(--church-gold)'"
        @mouseleave="$event.target.style.color = 'var(--church-navy)'"
      >
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
        </svg>
        교회 웹사이트에서 원문 보기
      </a>

      <!-- 자료 생성 안내 -->
      <div v-if="!store.generatedMaterial" class="mt-6 p-4 rounded-lg border-l-4" style="background-color: rgba(184, 134, 11, 0.08); border-color: var(--church-gold);">
        <p class="text-sm flex items-start" style="color: var(--church-navy);">
          <svg class="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" style="color: var(--church-gold);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>
            좌측의 <strong>'공과 자료 생성'</strong> 버튼을 클릭하여 선택한 대상 그룹에 맞는 공과 준비 자료를 생성하세요.
          </span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCurriculumStore } from '../stores/curriculum'

const store = useCurriculumStore()
const isContentExpanded = ref(false)
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
