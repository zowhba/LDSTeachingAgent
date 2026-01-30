<template>
  <div class="min-h-screen" style="background-color: var(--church-cream);">
    <!-- 헤더 -->
    <header class="bg-white shadow-sm border-b" style="border-color: var(--church-light-gray);">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- 상단 라인 (골드 악센트) -->
        <div class="h-1" style="background: linear-gradient(90deg, var(--church-gold), var(--church-gold-light), var(--church-gold));"></div>
        
        <div class="py-5">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <!-- 교회 로고 스타일 아이콘 -->
              <div class="w-12 h-12 rounded-full flex items-center justify-center" style="background-color: var(--church-navy);">
                <svg class="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
              </div>
              <div>
                <h1 class="text-xl sm:text-2xl font-semibold" style="color: var(--church-navy);">
                  공과 준비 도우미
                </h1>
                <p class="text-sm" style="color: var(--church-gray);">
                  후기성도 예수 그리스도 교회 · 신갈와드
                </p>
              </div>
            </div>
            <div class="hidden sm:block text-right">
              <span class="text-xs px-3 py-1 rounded-full" style="background-color: var(--church-cream); color: var(--church-navy);">
                v2.0
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 로딩 상태 -->
    <div v-if="store.isLoading" class="flex items-center justify-center h-96">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-10 w-10 border-3" 
             style="border-color: var(--church-light-gray); border-top-color: var(--church-navy);"></div>
        <p class="mt-4 text-sm" style="color: var(--church-gray);">데이터를 불러오는 중입니다...</p>
      </div>
    </div>

    <!-- 에러 메시지 -->
    <div v-else-if="store.error" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="card-church p-6" style="border-left: 4px solid #dc2626;">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div class="ml-4">
            <h3 class="text-base font-medium" style="color: var(--church-navy);">오류가 발생했습니다</h3>
            <p class="mt-1 text-sm" style="color: var(--church-gray);">{{ store.error }}</p>
            <button 
              @click="store.clearError()"
              class="mt-3 text-sm font-medium btn-church-secondary px-4 py-2 rounded-lg"
            >
              닫기
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 메인 컨텐츠 -->
    <main v-else class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-12 gap-6 lg:gap-8">
        <!-- 좌측 사이드바: 설정 -->
        <aside class="col-span-12 lg:col-span-3">
          <SettingsPanel />
        </aside>

        <!-- 우측 메인 영역: 공과 내용 & 자료 -->
        <section class="col-span-12 lg:col-span-9 space-y-6">
          <!-- 공과 정보 -->
          <LessonContent />
          
          <!-- 생성된 자료 -->
          <GeneratedMaterial v-if="store.generatedMaterial" />
          
          <!-- 채팅 -->
          <ChatSection v-if="store.generatedMaterial" />
        </section>
      </div>
    </main>

    <!-- 푸터 -->
    <footer class="mt-16 py-8 border-t" style="background-color: var(--church-navy); border-color: var(--church-navy-dark);">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <p class="text-sm" style="color: rgba(255,255,255,0.7);">
            © 2025 공과 준비 도우미
          </p>
          <p class="text-xs mt-2" style="color: rgba(255,255,255,0.5);">
            후기성도 예수 그리스도 교회의 교리에 기반한 공과 준비 도구입니다
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCurriculumStore } from './stores/curriculum'
import SettingsPanel from './components/SettingsPanel.vue'
import LessonContent from './components/LessonContent.vue'
import GeneratedMaterial from './components/GeneratedMaterial.vue'
import ChatSection from './components/ChatSection.vue'

const store = useCurriculumStore()

onMounted(() => {
  store.loadInitialData()
})
</script>
