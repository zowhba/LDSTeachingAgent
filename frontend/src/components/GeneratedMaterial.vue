<template>
  <div class="card-church overflow-hidden">
    <!-- 헤더 -->
    <div class="px-6 py-4 border-b" style="background: linear-gradient(135deg, var(--church-navy) 0%, var(--church-navy-light) 100%); border-color: var(--church-navy-dark);">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <div class="w-10 h-10 rounded-full flex items-center justify-center mr-4" style="background-color: rgba(255,255,255,0.15);">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-semibold text-white">공과 준비 자료</h2>
            <p class="text-sm" style="color: rgba(255,255,255,0.7);">
              {{ store.targetAudience }} 대상
            </p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <button 
            v-if="store.isAdmin" 
            @click="store.removeMaterial()"
            class="px-3 py-1 text-xs rounded-full border border-red-300 text-red-100 hover:bg-red-600 transition"
            style="background-color: rgba(220, 38, 38, 0.4);"
          >
            자료 삭제
          </button>

          <!-- 프리젠테이션 다운로드 버튼 -->
          <button
            v-if="store.isPresentationGenerating"
            disabled
            class="flex items-center px-3 py-1.5 text-xs rounded-full text-white font-semibold"
            style="background-color: rgba(201, 162, 39, 0.5);"
          >
            <svg class="animate-spin w-3.5 h-3.5 mr-1.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            발표자료 생성 중...
          </button>
          <button
            v-else-if="store.presentationHtml"
            @click="downloadPresentation"
            class="flex items-center px-3 py-1.5 text-xs rounded-full text-white font-semibold hover:opacity-90 transition"
            style="background-color: rgba(201, 162, 39, 0.85);"
          >
            <svg class="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            발표자료 다운로드
          </button>

          <span 
            v-if="store.isCachedMaterial"
            class="px-3 py-1 text-xs rounded-full"
            style="background-color: rgba(255,255,255,0.2); color: white;"
          >
            저장된 자료
          </span>
        </div>
      </div>
    </div>

    <!-- 자료 내용 -->
    <div class="p-6">
      <!-- 툴바 -->
      <div class="flex items-center justify-between mb-5 pb-4 border-b" style="border-color: var(--church-light-gray);">
        <div class="flex items-center space-x-2">
          <button
            @click="expandAll"
            class="flex items-center px-3 py-2 text-sm rounded-lg transition border"
            style="border-color: var(--church-border); color: var(--church-gray);"
          >
            <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
            모두 펼치기
          </button>
          <button
            @click="collapseAll"
            class="flex items-center px-3 py-2 text-sm rounded-lg transition border"
            style="border-color: var(--church-border); color: var(--church-gray);"
          >
            <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
            </svg>
            모두 접기
          </button>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="copyToClipboard"
            class="flex items-center px-3 py-2 text-sm rounded-lg transition border"
            style="border-color: var(--church-border); color: var(--church-gray);"
          >
            <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
            </svg>
            {{ copyButtonText }}
          </button>
          <button
            @click="toggleRawView"
            class="flex items-center px-3 py-2 text-sm rounded-lg transition border"
            style="border-color: var(--church-border); color: var(--church-gray);"
          >
            <svg v-if="!showRawView" class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            <svg v-else class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            {{ showRawView ? '섹션 보기' : '원본 보기' }}
          </button>
        </div>
      </div>

      <!-- 원본 보기 -->
      <div v-if="showRawView">
        <pre 
          class="p-4 rounded-lg overflow-x-auto text-sm whitespace-pre-wrap font-mono leading-relaxed"
          style="background-color: var(--church-cream); color: var(--church-gray);"
        >{{ store.generatedMaterial }}</pre>
      </div>

      <!-- 섹션별 보기 -->
      <div v-else class="space-y-3">
        <div 
          v-for="(section, index) in parsedSections" 
          :key="index"
          class="border rounded-lg overflow-hidden"
          style="border-color: var(--church-light-gray);"
        >
          <!-- 섹션 헤더 -->
          <button
            @click="toggleSection(index)"
            class="w-full px-4 py-3 flex items-center justify-between transition-colors"
            :style="{
              backgroundColor: expandedSections[index] ? 'var(--church-navy)' : 'white',
              color: expandedSections[index] ? 'white' : 'var(--church-navy)'
            }"
          >
            <div class="flex items-center">
              <span class="w-8 h-8 rounded-full flex items-center justify-center mr-3 text-sm font-medium"
                    :style="{
                      backgroundColor: expandedSections[index] ? 'rgba(255,255,255,0.2)' : 'var(--church-cream)',
                      color: expandedSections[index] ? 'white' : 'var(--church-navy)'
                    }">
                {{ getSectionIcon(section.title) }}
              </span>
              <span class="font-semibold text-left">{{ section.title }}</span>
            </div>
            <svg 
              :class="['w-5 h-5 transition-transform duration-200', expandedSections[index] ? 'rotate-180' : '']"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <!-- 섹션 내용 -->
          <transition name="accordion">
            <div 
              v-show="expandedSections[index]"
              class="px-5 py-4 border-t"
              style="background-color: white; border-color: var(--church-light-gray);"
            >
              <div 
                class="markdown-content prose prose-lg max-w-none"
                v-html="renderMarkdown(section.content)"
              ></div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'
import { useCurriculumStore } from '../stores/curriculum'

const store = useCurriculumStore()

const showRawView = ref(false)
const copyButtonText = ref('복사')
const expandedSections = ref({})

// 섹션 아이콘 매핑
const sectionIcons = {
  '공과 개요': '📋',
  '도입부': '🎯',
  '역사적 배경': '📜',
  '본론': '📖',
  '심층 교리': '📖',
  '토론 질문': '💬',
  '예상 질문': '❓',
  'FAQ': '❓',
  '활동': '🎮',
  '결론': '✨',
  '추가 자료': '📚'
}

function getSectionIcon(title) {
  for (const [key, icon] of Object.entries(sectionIcons)) {
    if (title.includes(key)) return icon
  }
  return '📄'
}

// 마크다운을 섹션으로 파싱
const parsedSections = computed(() => {
  if (!store.generatedMaterial) return []
  
  const content = store.generatedMaterial
  const sections = []
  
  // ## 로 시작하는 섹션 분리
  const regex = /^## (.+)$/gm
  let match
  let lastIndex = 0
  const matches = []
  
  while ((match = regex.exec(content)) !== null) {
    matches.push({
      title: match[1].trim(),
      index: match.index,
      length: match[0].length
    })
  }
  
  for (let i = 0; i < matches.length; i++) {
    const current = matches[i]
    const next = matches[i + 1]
    
    const startContent = current.index + current.length
    const endContent = next ? next.index : content.length
    const sectionContent = content.slice(startContent, endContent).trim()
    
    sections.push({
      title: current.title,
      content: sectionContent
    })
  }
  
  // 섹션이 없으면 전체를 하나의 섹션으로
  if (sections.length === 0) {
    sections.push({
      title: '공과 자료',
      content: content
    })
  }
  
  return sections
})

// 섹션이 변경되면 확장 상태 초기화
watch(parsedSections, (newSections) => {
  const newExpanded = {}
  newSections.forEach((_, index) => {
    // 기본적으로 첫 번째와 두 번째 섹션만 펼침
    newExpanded[index] = index < 2
  })
  expandedSections.value = newExpanded
}, { immediate: true })

function toggleSection(index) {
  expandedSections.value[index] = !expandedSections.value[index]
}

function expandAll() {
  const expanded = {}
  parsedSections.value.forEach((_, index) => {
    expanded[index] = true
  })
  expandedSections.value = expanded
}

function collapseAll() {
  const collapsed = {}
  parsedSections.value.forEach((_, index) => {
    collapsed[index] = false
  })
  expandedSections.value = collapsed
}

function toggleRawView() {
  showRawView.value = !showRawView.value
}

function renderMarkdown(content) {
  if (!content) return ''
  
  // ~ 기호를 삭제선으로 해석하지 않도록 모든 ~ 기호를 전각 기호(～)로 치환
  // (공과 자료에서 날짜나 장 구분에 사용된 ~가 취소선으로 변환되는 렌더링 버그 방지)
  const escapedContent = content.replace(/~/g, '～')
  
  marked.setOptions({
    breaks: true,
    gfm: true
  })
  
  return marked(escapedContent)
}

async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(store.generatedMaterial)
    copyButtonText.value = '복사됨!'
    setTimeout(() => {
      copyButtonText.value = '복사'
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
    copyButtonText.value = '복사 실패'
  }
}

function downloadPresentation() {
  if (!store.presentationHtml) return

  const lessonTitle = store.lessonData?.title || '공과자료'
  const weekRange = store.weekRange || ''
  const filename = `[발표자료] ${lessonTitle} (${weekRange}).html`

  const blob = new Blob([store.presentationHtml], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.accordion-enter-active,
.accordion-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.accordion-enter-from,
.accordion-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.accordion-enter-to,
.accordion-leave-from {
  opacity: 1;
  max-height: 2000px;
}
</style>
