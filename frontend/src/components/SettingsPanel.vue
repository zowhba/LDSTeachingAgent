<template>
  <div class="space-y-4 mb-8">
    <!-- 설정 패널 전체 컨테이너 (시각적 구분 강화) -->
    <div class="relative bg-white rounded-2xl p-5 sm:p-7 shadow-[0_8px_30px_rgb(0,0,0,0.08)] border border-gray-200 overflow-hidden">
      
      <!-- 상단 데코레이션 라인 -->
      <div class="absolute top-0 left-0 w-full h-1.5" style="background: linear-gradient(90deg, var(--church-navy), #2563eb, var(--church-gold));"></div>
      
      <!-- 가로형 레이아웃 바 (Grid로 정확한 3:2:5 비율 적용) -->
      <div class="grid grid-cols-1 lg:grid-cols-10 items-end gap-4 lg:gap-6">
        
        <!-- 1. 주차 선택 (3/10 비율) -->
        <div class="w-full lg:col-span-3">
          <label class="flex items-center text-xs font-semibold mb-2 uppercase tracking-wider" style="color: var(--church-navy);">
            <svg class="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            공과 주차
          </label>
          <select 
            :value="store.selectedWeekIndex"
            @change="onWeekChange($event)"
            class="w-full px-4 py-2 text-sm bg-white/80 border border-gray-200 rounded-xl shadow-sm hover:shadow-md hover:bg-white hover:border-blue-300 focus:ring-4 focus:ring-blue-100 focus:border-blue-400 focus:outline-none transition-all duration-200 cursor-pointer backdrop-blur-sm font-medium"
            style="color: var(--church-navy); height: 44px;"
          >
            <option 
              v-for="(week, index) in store.weeks" 
              :key="index" 
              :value="index"
              :class="index < store.currentWeekIndex ? 'text-gray-400 italic' : ''"
            >
              {{ index < store.currentWeekIndex ? '✓ ' : (index === store.currentWeekIndex ? '▶ ' : '') }}{{ week.display_text }}
            </option>
          </select>
        </div>

        <!-- 2. 대상 선택 (2/10 비율) -->
        <div class="w-full lg:col-span-2">
          <label class="flex items-center text-xs font-semibold mb-2 uppercase tracking-wider" style="color: var(--church-navy);">
            <svg class="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            대상 그룹
          </label>
          <select 
            :value="store.targetAudience"
            @change="store.setTargetAudience($event.target.value)"
            class="w-full px-4 py-2 text-sm bg-white/80 border border-gray-200 rounded-xl shadow-sm hover:shadow-md hover:bg-white hover:border-blue-300 focus:ring-4 focus:ring-blue-100 focus:border-blue-400 focus:outline-none transition-all duration-200 cursor-pointer backdrop-blur-sm font-medium"
            style="color: var(--church-navy); height: 44px;"
          >
            <option 
              v-for="audience in store.targetAudiences" 
              :key="audience" 
              :value="audience"
            >
              {{ getAudienceIcon(audience) }} {{ audience }}
            </option>
          </select>
        </div>

        <!-- 3. 질문 기록 (5/10 비율) -->
        <div class="w-full lg:col-span-5">
          <label class="flex items-center justify-between text-xs font-semibold mb-2 uppercase tracking-wider" style="color: var(--church-navy);">
            <div class="flex items-center">
              <svg class="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              이전 질문 확인
            </div>
            <span v-if="store.qaList.length > 0" class="text-[10px] px-1.5 py-0.5 rounded-full" style="background-color: var(--church-cream); color: var(--church-navy);">
              {{ store.qaList.length }}개의 기록
            </span>
          </label>
          <select 
            v-model="selectedQAIndex"
            class="w-full px-4 py-2 text-sm bg-white/80 border border-gray-200 rounded-xl shadow-sm hover:shadow-md hover:bg-white hover:border-blue-300 focus:ring-4 focus:ring-blue-100 focus:border-blue-400 focus:outline-none transition-all duration-200 cursor-pointer backdrop-blur-sm font-medium"
            style="color: var(--church-navy); height: 44px;"
          >
            <option :value="null" disabled>질문 기록을 선택하세요 (콤보박스 선택 시 상세 내용이 아래에 표시됩니다)</option>
            <option 
              v-for="(qa, index) in store.qaList" 
              :key="index" 
              :value="index"
            >
              {{ store.qaList.length - index }}. {{ truncate(qa.question, 80) }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- 선택된 질문 표시 영역 (가시성 강화) -->
    <transition name="fade">
      <div v-if="selectedQAIndex !== null && store.qaList[selectedQAIndex]" class="card-church overflow-hidden border-2" style="border-color: var(--church-gold-light); background-color: white;">
        <div class="flex items-center justify-between px-5 py-3 border-b" style="background-color: var(--church-cream); border-color: var(--church-gold-light);">
          <div class="flex items-center">
            <span class="w-7 h-7 rounded-full flex items-center justify-center mr-3 text-sm font-bold shadow-sm" style="background-color: var(--church-navy); color: white;">Q</span>
            <span class="font-bold text-sm" style="color: var(--church-navy);">선택된 질문 내용</span>
          </div>
          <div class="flex items-center space-x-2">
            <button 
              v-if="store.isAdmin" 
              @click.stop="confirmRemoveQA"
              class="text-xs px-2 py-1 rounded border border-red-200 text-red-500 hover:bg-red-50"
            >
              기록 삭제
            </button>
            <button @click="selectedQAIndex = null" class="text-gray-400 hover:text-gray-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l18 18" />
              </svg>
            </button>
          </div>
        </div>
        <div class="p-6">
          <div class="bg-gray-50 rounded-xl p-5 mb-5 shadow-inner">
            <p class="text-lg font-medium leading-relaxed" style="color: var(--church-navy);">
              {{ store.qaList[selectedQAIndex].question }}
            </p>
          </div>
          <div class="flex items-start">
            <span class="w-7 h-7 rounded-full flex items-center justify-center mr-3 text-sm font-bold shadow-sm flex-shrink-0 mt-1" style="background-color: var(--church-gold); color: white;">A</span>
            <div class="text-base leading-loose whitespace-pre-wrap" style="color: var(--church-gray);">
              {{ store.qaList[selectedQAIndex].answer }}
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useCurriculumStore } from '../stores/curriculum'

const store = useCurriculumStore()
const selectedQAIndex = ref(null)

// 주차나 대상 그룹이 바뀌면 선택된 질문 초기화
watch(() => [store.selectedWeekIndex, store.targetAudience], () => {
  selectedQAIndex.value = null
})

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

function confirmRemoveQA() {
  const item = store.qaList[selectedQAIndex.value]
  if (item) {
    store.removeQA(item)
    selectedQAIndex.value = null
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
