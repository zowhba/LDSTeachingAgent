<template>
  <div class="card-church p-6 sticky top-6">
    <!-- 헤더 -->
    <div class="flex items-center mb-6 pb-4 border-b" style="border-color: var(--church-light-gray);">
      <div class="w-8 h-8 rounded-full flex items-center justify-center mr-3" style="background-color: var(--church-cream);">
        <svg class="w-4 h-4" style="color: var(--church-navy);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </div>
      <h2 class="text-lg font-semibold" style="color: var(--church-navy);">설정</h2>
    </div>

    <!-- 주차 선택 -->
    <div class="mb-6">
      <label class="block text-sm font-medium mb-2" style="color: var(--church-navy);">
        공과 주차
      </label>
      <select 
        :value="store.selectedWeekIndex"
        @change="onWeekChange($event)"
        class="w-full px-4 py-3 input-church text-sm"
        style="color: var(--church-gray);"
      >
        <option 
          v-for="(week, index) in store.weeks" 
          :key="index" 
          :value="index"
        >
          {{ week.display_text }}
        </option>
      </select>
    </div>

    <!-- 대상 선택 -->
    <div class="mb-6">
      <label class="block text-sm font-medium mb-3" style="color: var(--church-navy);">
        대상 그룹
      </label>
      <div class="space-y-2">
        <button
          v-for="audience in store.targetAudiences"
          :key="audience"
          @click="store.setTargetAudience(audience)"
          :class="[
            'w-full px-4 py-2.5 rounded-lg text-sm font-medium transition-all text-left flex items-center',
            store.targetAudience === audience
              ? 'selected-church'
              : 'bg-white border hover:border-gray-400'
          ]"
          :style="store.targetAudience !== audience ? { borderColor: 'var(--church-border)', color: 'var(--church-gray)' } : {}"
        >
          <span class="w-6 h-6 rounded-full flex items-center justify-center mr-3 text-xs"
                :style="store.targetAudience === audience 
                  ? { backgroundColor: 'rgba(255,255,255,0.2)' } 
                  : { backgroundColor: 'var(--church-cream)' }">
            {{ getAudienceIcon(audience) }}
          </span>
          {{ audience }}
          <svg v-if="store.targetAudience === audience" 
               class="w-4 h-4 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 자료 생성 버튼 -->
    <button
      @click="store.generateMaterial()"
      :disabled="store.isGenerating || !store.lessonData"
      class="w-full py-3.5 px-6 btn-church-primary font-medium rounded-lg disabled:cursor-not-allowed flex items-center justify-center"
    >
      <span v-if="store.isGenerating" class="flex items-center">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        자료 생성 중...
      </span>
      <span v-else class="flex items-center">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        공과 자료 생성
      </span>
    </button>

    <!-- 구분선 -->
    <div class="my-6 border-t" style="border-color: var(--church-light-gray);"></div>

    <!-- Q&A 히스토리 -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-medium flex items-center" style="color: var(--church-navy);">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          질문 기록
        </h3>
        <span v-if="store.qaList.length > 0" class="text-xs px-2 py-0.5 rounded-full" style="background-color: var(--church-cream); color: var(--church-navy);">
          {{ store.qaList.length }}
        </span>
      </div>
      
      <div v-if="store.qaList.length === 0" class="text-center py-6">
        <div class="w-12 h-12 mx-auto rounded-full flex items-center justify-center mb-3" style="background-color: var(--church-cream);">
          <svg class="w-6 h-6" style="color: var(--church-gray);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p class="text-sm" style="color: var(--church-gray);">
          아직 질문이 없습니다
        </p>
        <p class="text-xs mt-1" style="color: var(--church-gray); opacity: 0.7;">
          공과 자료에 대한 질문을 해보세요
        </p>
      </div>
      
      <div v-else class="space-y-2 max-h-56 overflow-y-auto">
        <details
          v-for="(qa, index) in store.qaList"
          :key="index"
          class="group rounded-lg overflow-hidden border"
          style="border-color: var(--church-light-gray);"
        >
          <summary class="px-3 py-2.5 cursor-pointer hover:bg-gray-50 transition text-sm flex items-center" style="color: var(--church-gray);">
            <span class="w-5 h-5 rounded-full flex items-center justify-center mr-2 text-xs flex-shrink-0" style="background-color: var(--church-navy); color: white;">
              {{ store.qaList.length - index }}
            </span>
            <span class="truncate flex-1">{{ truncate(qa.question, 25) }}</span>
            <svg class="w-4 h-4 ml-2 transition-transform group-open:rotate-180 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </summary>
          <div class="px-3 py-3 border-t text-sm" style="background-color: var(--church-cream); border-color: var(--church-light-gray);">
            <p class="mb-2" style="color: var(--church-navy);">
              <strong>Q:</strong> {{ qa.question }}
            </p>
            <p style="color: var(--church-gray);">
              <strong style="color: var(--church-gold);">A:</strong> {{ qa.answer }}
            </p>
          </div>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useCurriculumStore } from '../stores/curriculum'

const store = useCurriculumStore()

function onWeekChange(event) {
  store.selectWeek(Number(event.target.value))
}

function truncate(text, maxLength) {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

function getAudienceIcon(audience) {
  const icons = {
    '성인': '👥',
    '신회원': '🌱',
    '청소년': '🎓',
    '초등회': '🧒'
  }
  return icons[audience] || '👤'
}
</script>
