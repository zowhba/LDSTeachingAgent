<template>
  <div class="min-h-screen" style="background-color: var(--church-cream);">
    <!-- 헤더 -->
    <header class="bg-white shadow-sm border-b" style="border-color: var(--church-light-gray);">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- 상단 라인 (골드 악센트) -->
        <div class="h-1" style="background: linear-gradient(90deg, var(--church-gold), var(--church-gold-light), var(--church-gold));"></div>
        
        <div class="py-5">
          <div class="flex items-center justify-between gap-4">
            <!-- 1. 좌측: 교회 로고 스타일 아이콘 + 타이틀 -->
            <div class="flex items-center space-x-4 flex-shrink-0">
              <div class="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0" style="background-color: var(--church-navy);">
                <svg class="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
              </div>
              <div class="hidden sm:block">
                <h1 class="text-xl font-semibold leading-tight" style="color: var(--church-navy);">
                  공과 준비 도우미 <span v-if="store.isAdmin" class="text-sm font-normal text-red-500 ml-1">(관리자)</span>
                </h1>
                <p class="text-[10px]" style="color: var(--church-gray);">
                  후기성도 예수 그리스도 교회 신갈와드
                </p>
              </div>
            </div>

            <!-- 2. 중앙~우측: GNB 메뉴 (ml-auto로 우측 정렬) -->
            <nav class="hidden md:flex items-center space-x-6 lg:space-x-10 ml-auto mr-4 lg:mr-8">
              <button 
                v-for="menu in menus" 
                :key="menu.id"
                @click="store.setMenu(menu.id)"
                class="h-12 text-sm font-bold transition-all relative flex items-center px-1"
                :style="{
                  color: store.currentMenu === menu.id ? 'var(--church-navy)' : 'var(--church-gray)'
                }"
              >
                {{ menu.label }}
                <div 
                  v-if="store.currentMenu === menu.id" 
                  class="absolute bottom-0 left-0 right-0 h-0.5 rounded-full"
                  style="background-color: var(--church-gold);"
                ></div>
              </button>
            </nav>

            <!-- 3. 우측: 버튼 영역 -->
            <div class="flex items-center space-x-3 flex-shrink-0">
              <button 
                v-if="store.isAdmin" 
                @click="store.logoutAdmin()"
                class="text-xs px-3 py-1.5 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition"
              >
                로그아웃
              </button>
              <div class="hidden sm:block text-right">
                <span class="text-[10px] px-2 py-0.5 rounded-full border border-gray-200" style="background-color: var(--church-cream); color: var(--church-navy);">
                  v2.5
                </span>
              </div>
            </div>
          </div>
          
          <!-- 모바일 GNB 메뉴 (스크린이 작을 때만 하단에 표시) -->
          <nav class="flex md:hidden items-center justify-around mt-4 pt-4 border-t border-gray-50">
            <button 
              v-for="menu in menus" 
              :key="menu.id"
              @click="store.setMenu(menu.id)"
              class="text-xs font-bold transition-all px-2 py-1 rounded"
              :style="{
                backgroundColor: store.currentMenu === menu.id ? 'var(--church-cream)' : 'transparent',
                color: store.currentMenu === menu.id ? 'var(--church-navy)' : 'var(--church-gray)'
              }"
            >
              {{ menu.label }}
            </button>
          </nav>
        </div>
      </div>
    </header>

    <!-- 관리자 로그인 모달 -->
    <div v-if="showAdminModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div class="bg-white rounded-xl shadow-2xl max-w-sm w-full p-6">
        <div class="text-center mb-6">
          <div class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 class="text-xl font-bold text-gray-900">관리자 인증</h2>
          <p class="text-sm text-gray-500 mt-1">비밀번호를 입력해주세요</p>
        </div>
        
        <form @submit.prevent="handleLogin">
          <input 
            v-model="adminPassword" 
            type="password" 
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition"
            placeholder="비밀번호"
            autofocus
          />
          <div v-if="loginError" class="mt-2 text-xs text-red-500">{{ loginError }}</div>
          
          <div class="grid grid-cols-2 gap-3 mt-6">
            <button 
              type="button" 
              @click="closeModal"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
            >
              취소
            </button>
            <button 
              type="submit"
              class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 shadow-sm transition"
            >
              로그인
            </button>
          </div>
        </form>
      </div>
    </div>

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

    <!-- 메인 컨텐츠 영역 (메뉴에 따라 전환) -->
    <main v-else class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <transition name="fade-view" mode="out-in">
        <!-- 1. 소개 페이지 -->
        <AboutView v-if="store.currentMenu === 'about'" />
        
        <!-- 2. 공과보조 자료 (기존 메인) -->
        <div v-else-if="store.currentMenu === 'lesson'" class="space-y-6">
          <SettingsPanel />
          <div class="space-y-6 w-full">
            <LessonContent />
            <GeneratedMaterial v-if="store.generatedMaterial" />
            <ChatSection v-if="store.generatedMaterial" />
          </div>
        </div>

        <!-- 3. 문의 페이지 -->
        <ContactView v-else-if="store.currentMenu === 'contact'" />
      </transition>
    </main>

    <!-- 푸터 -->
    <footer class="mt-16 py-8 border-t" style="background-color: var(--church-navy); border-color: var(--church-navy-dark);">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <p class="text-sm" style="color: rgba(255,255,255,0.7);">
            © 2026 공과 준비 도우미
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
import { onMounted, ref, computed } from 'vue'
import { useCurriculumStore } from './stores/curriculum'
import SettingsPanel from './components/SettingsPanel.vue'
import LessonContent from './components/LessonContent.vue'
import GeneratedMaterial from './components/GeneratedMaterial.vue'
import ChatSection from './components/ChatSection.vue'
import AboutView from './components/AboutView.vue'
import ContactView from './components/ContactView.vue'

const store = useCurriculumStore()
const adminPassword = ref('')
const loginError = ref('')

const menus = [
  { id: 'about', label: '소개' },
  { id: 'lesson', label: '공과보조 자료' },
  { id: 'contact', label: '게시판' }
]

const showAdminModal = computed(() => {
  return store.isAdminPath && !store.isAdmin
})

onMounted(() => {
  store.loadInitialData()
})

async function handleLogin() {
  loginError.value = ''
  if (!adminPassword.value) {
    loginError.value = '비밀번호를 입력해주세요.'
    return
  }
  
  const success = await store.loginAsAdmin(adminPassword.value)
  if (success) {
    adminPassword.value = ''
  } else {
    loginError.value = '비밀번호가 올바르지 않습니다.'
  }
}

function closeModal() {
  window.location.href = '/'
}
</script>

<style>
.fade-view-enter-active, .fade-view-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-view-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-view-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
