<template>
  <div class="card-church overflow-hidden">
    <!-- 헤더 -->
    <div class="px-6 py-4 border-b" style="background-color: white; border-color: var(--church-light-gray);">
      <div class="flex items-center">
        <div class="w-10 h-10 rounded-full flex items-center justify-center mr-4" style="background-color: var(--church-cream);">
          <svg class="w-5 h-5" style="color: var(--church-navy);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-semibold" style="color: var(--church-navy);">질문하기</h2>
          <p class="text-sm" style="color: var(--church-gray);">공과 자료에 대해 궁금한 점을 물어보세요</p>
        </div>
      </div>
    </div>

    <!-- 채팅 영역 -->
    <div class="p-6" style="background-color: var(--church-cream);">
      <!-- 채팅 히스토리 -->
      <div 
        ref="chatContainer"
        class="space-y-4 max-h-80 overflow-y-auto mb-5 scroll-smooth"
      >
        <!-- 빈 상태 -->
        <div v-if="store.chatHistory.length === 0" class="text-center py-8">
          <div class="w-16 h-16 mx-auto rounded-full flex items-center justify-center mb-4" style="background-color: white;">
            <svg class="w-8 h-8" style="color: var(--church-gold);" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-sm mb-4" style="color: var(--church-gray);">
            공과 자료에 대해 궁금한 점을 물어보세요
          </p>
          <div class="flex flex-wrap justify-center gap-2">
            <button
              v-for="suggestion in suggestions"
              :key="suggestion"
              @click="sendMessage(suggestion)"
              class="px-3 py-1.5 text-xs rounded-full transition border"
              style="background-color: white; border-color: var(--church-border); color: var(--church-navy);"
              @mouseenter="$event.target.style.backgroundColor = 'var(--church-navy)'; $event.target.style.color = 'white'"
              @mouseleave="$event.target.style.backgroundColor = 'white'; $event.target.style.color = 'var(--church-navy)'"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>

        <!-- 메시지들 -->
        <div 
          v-for="(message, index) in store.chatHistory" 
          :key="index"
          :class="[
            'flex',
            message.role === 'user' ? 'justify-end' : 'justify-start'
          ]"
        >
          <div 
            :class="[
              'max-w-[85%] px-4 py-3 shadow-sm',
              message.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'
            ]"
          >
            <p class="text-sm leading-relaxed whitespace-pre-wrap">
              {{ message.content }}
            </p>
          </div>
        </div>

        <!-- 로딩 상태 -->
        <div v-if="store.isChatLoading" class="flex justify-start">
          <div class="chat-bubble-assistant px-4 py-3 shadow-sm">
            <div class="flex items-center space-x-2">
              <div class="flex space-x-1">
                <div class="w-2 h-2 rounded-full animate-bounce" style="background-color: var(--church-navy); animation-delay: 0ms"></div>
                <div class="w-2 h-2 rounded-full animate-bounce" style="background-color: var(--church-navy); animation-delay: 150ms"></div>
                <div class="w-2 h-2 rounded-full animate-bounce" style="background-color: var(--church-navy); animation-delay: 300ms"></div>
              </div>
              <span class="text-xs" style="color: var(--church-gray);">답변 생성 중...</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 입력 영역 -->
      <form @submit.prevent="handleSubmit" class="flex gap-3">
        <input
          v-model="userInput"
          type="text"
          placeholder="질문을 입력하세요..."
          :disabled="store.isChatLoading"
          class="flex-1 px-4 py-3 text-sm input-church disabled:opacity-50"
          style="background-color: white;"
          @keydown.enter.prevent="handleSubmit"
        />
        <button
          type="submit"
          :disabled="!userInput.trim() || store.isChatLoading"
          class="px-5 py-3 btn-church-primary font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
        >
          <span v-if="store.isChatLoading">
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </span>
          <span v-else class="flex items-center">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { useCurriculumStore } from '../stores/curriculum'

const store = useCurriculumStore()
const userInput = ref('')
const chatContainer = ref(null)

const suggestions = [
  '핵심 메시지는?',
  '토론 질문 추천',
  '적용 방법은?',
  '관련 경전 구절'
]

async function handleSubmit() {
  if (!userInput.value.trim() || store.isChatLoading) return
  
  const question = userInput.value.trim()
  userInput.value = ''
  
  await store.sendChatMessage(question)
  
  await nextTick()
  scrollToBottom()
}

function sendMessage(message) {
  userInput.value = message
  handleSubmit()
}

function scrollToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

watch(() => store.chatHistory.length, () => {
  nextTick(scrollToBottom)
})
</script>

<style scoped>
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}
.animate-bounce {
  animation: bounce 0.6s infinite;
}
</style>
