/**
 * Pinia Store - 공과 상태 관리
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '../api'

export const useCurriculumStore = defineStore('curriculum', () => {
  // 상태
  const weeks = ref([])
  const currentWeekIndex = ref(0)
  const selectedWeekIndex = ref(0)
  const targetAudience = ref('성인')
  // const targetAudiences = ref(['성인', '신회원', '청소년', '초등회'])
  const targetAudiences = ref(['성인', '초등회'])

  const lessonData = ref(null)
  const generatedMaterial = ref('')
  const isGenerating = ref(false)
  const isCachedMaterial = ref(false)

  const presentationHtml = ref('')
  const isPresentationGenerating = ref(false)

  const qaList = ref([])
  const chatHistory = ref([])
  const isChatLoading = ref(false)

  const isLoading = ref(true)
  const error = ref(null)

  // GNB 메뉴 상태
  const currentMenu = ref('lesson') // 'about', 'lesson', 'contact'

  // 관리자 상태
  const isAdmin = ref(localStorage.getItem('isAdmin') === 'true')

  // Getters
  const selectedWeek = computed(() => weeks.value[selectedWeekIndex.value] || null)
  const weekRange = computed(() => selectedWeek.value?.week_range || '')
  const isAdminPath = computed(() => window.location.pathname === '/admin')

  // Actions
  async function loadInitialData() {
    isLoading.value = true
    error.value = null

    try {
      // 주차 목록과 현재 주차 정보 동시 로드
      const [weeksData, currentWeekData] = await Promise.all([
        api.getAvailableWeeks(),
        api.getCurrentWeek()
      ])

      weeks.value = weeksData
      currentWeekIndex.value = currentWeekData.index
      selectedWeekIndex.value = currentWeekData.index

      // 현재 주차의 공과 정보 로드
      if (selectedWeek.value) {
        await loadLessonData()
      }
    } catch (err) {
      error.value = '데이터를 불러오는 중 오류가 발생했습니다: ' + err.message
      console.error('Error loading initial data:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function loadLessonData() {
    if (!selectedWeek.value) return

    try {
      lessonData.value = await api.getCurriculumByWeek({
        start_date: selectedWeek.value.start_date,
        end_date: selectedWeek.value.end_date,
        week_range: selectedWeek.value.week_range
      })

      // Q&A 목록도 로드
      await loadQAList()

      // 저장된 공과 자료 자동 로드
      await checkCachedMaterial()
      
      // 만약 저장된 자료가 없다면 자동으로 생성 시작 (이 함수 내에서 프리젠테이션도 함께 호출됨)
      if (!generatedMaterial.value && !isGenerating.value) {
        console.log('📦 캐시된 자료가 없어 자동으로 생성을 시작합니다...')
        generateMaterial()
      } else if (generatedMaterial.value && !presentationHtml.value && !isPresentationGenerating.value) {
        console.log('📦 공과 자료는 있지만 프리젠테이션이 없어 자동으로 벡그라운드 생성을 시작합니다...')
        const requestData = {
          week_range: weekRange.value,
          target_audience: targetAudience.value,
          lesson_title: lessonData.value.title,
          lesson_content: lessonData.value.content
        }
        generatePresentationInBackground(requestData)
      }
    } catch (err) {
      console.error('Error loading lesson data:', err)
      error.value = '공과 정보를 불러오는 중 오류가 발생했습니다.'
    }
  }

  async function checkCachedMaterial() {
    if (!lessonData.value) return

    try {
      const result = await api.getCachedMaterial(
        weekRange.value,
        targetAudience.value,
        lessonData.value.title
      )

      if (result && result.material) {
        generatedMaterial.value = result.material
        isCachedMaterial.value = result.is_cached

        // 프리젠테이션 캐시도 확인
        if (result.material) {
          try {
            const presResult = await api.getCachedPresentation(
              weekRange.value,
              targetAudience.value,
              lessonData.value.title
            )
            if (presResult && presResult.html) {
              presentationHtml.value = presResult.html
            }
          } catch (e) {
            console.warn('프리젠테이션 캐시 확인 실패:', e)
          }
        }
      } else {
        generatedMaterial.value = ''
        isCachedMaterial.value = false
        presentationHtml.value = ''
      }
    } catch (err) {
      console.error('Error checking cached material:', err)
    }
  }

  async function selectWeek(index) {
    if (index === selectedWeekIndex.value) return

    // 주차 변경 시 기존 자료 초기화
    generatedMaterial.value = ''
    chatHistory.value = []
    isCachedMaterial.value = false

    selectedWeekIndex.value = index
    await loadLessonData()
  }

  async function setTargetAudience(audience) {
    if (audience === targetAudience.value) return

    // 대상 변경 시 기존 자료 초기화
    generatedMaterial.value = ''
    chatHistory.value = []
    isCachedMaterial.value = false

    targetAudience.value = audience

    // Q&A 로드 후 저장된 자료 자동 로드
    await loadQAList()
    await checkCachedMaterial()
  }

  async function generateMaterial() {
    if (!lessonData.value || isGenerating.value) return

    isGenerating.value = true
    error.value = null

    try {
      const requestData = {
        lesson_title: lessonData.value.title,
        lesson_content: lessonData.value.content,
        target_audience: targetAudience.value,
        week_range: weekRange.value
      }

      // 공과 자료 생성 (이것만 await - 타임아웃 없이 완료까지 대기)
      const result = await api.generateMaterial(requestData)
      generatedMaterial.value = result.material
      isCachedMaterial.value = result.is_cached

      // 프리젠테이션은 완전히 독립 백그라운드로 - UI를 막지 않음
      generatePresentationInBackground(requestData)

    } catch (err) {
      error.value = '공과 자료 생성 중 오류가 발생했습니다: ' + err.message
      console.error('Error generating material:', err)
    } finally {
      isGenerating.value = false
    }
  }

  async function generatePresentationInBackground(requestData) {
    if (isPresentationGenerating.value) return
    isPresentationGenerating.value = true
    presentationHtml.value = ''

    try {
      console.log('🎨 발표자료 백그라운드 생성 시작...')
      const result = await api.generatePresentation(requestData)
      if (result && result.html) {
        presentationHtml.value = result.html
        console.log('✅ 발표자료 생성 완료')
      }
    } catch (err) {
      // 발표자료 실패는 공과자료 표시에 영향 없음 - 조용히 처리
      console.warn('⚠️ 발표자료 생성 실패 (공과자료는 정상):', err.message)
    } finally {
      isPresentationGenerating.value = false
    }
  }


  async function sendChatMessage(question) {
    if (!lessonData.value || !generatedMaterial.value || isChatLoading.value) return

    isChatLoading.value = true

    // 사용자 메시지 추가
    chatHistory.value.push({
      role: 'user',
      content: question
    })

    try {
      const result = await api.sendChatMessage({
        lesson_title: lessonData.value.title,
        lesson_content: lessonData.value.content,
        reference_material: generatedMaterial.value,
        user_question: question,
        week_range: weekRange.value,
        target_audience: targetAudience.value
      })

      // AI 응답 추가
      chatHistory.value.push({
        role: 'assistant',
        content: result.answer
      })

      // Q&A 목록 새로고침
      await loadQAList()

    } catch (err) {
      chatHistory.value.push({
        role: 'assistant',
        content: '답변 생성 중 오류가 발생했습니다. 다시 시도해주세요.'
      })
      console.error('Error sending chat message:', err)
    } finally {
      isChatLoading.value = false
    }
  }

  async function loadQAList() {
    if (!weekRange.value) return

    try {
      qaList.value = await api.getQAList(weekRange.value, targetAudience.value)
    } catch (err) {
      console.error('Error loading QA list:', err)
    }
  }

  async function loginAsAdmin(password) {
    try {
      const result = await api.adminLogin(password)
      if (result.success) {
        isAdmin.value = true
        localStorage.setItem('isAdmin', 'true')
        return true
      }
      return false
    } catch (err) {
      console.error('Admin login error:', err)
      return false
    }
  }

  function logoutAdmin() {
    isAdmin.value = false
    localStorage.removeItem('isAdmin')
    window.location.href = '/'
  }

  async function removeMaterial() {
    if (!lessonData.value || !isAdmin.value) return

    if (!confirm('정말로 이 공과 자료를 삭제하시겠습니까?')) return

    try {
      await api.deleteMaterial({
        lesson_title: lessonData.value.title,
        week_range: weekRange.value,
        target_audience: targetAudience.value
      })
      generatedMaterial.value = ''
      isCachedMaterial.value = false
      alert('자료가 삭제되었습니다.')
    } catch (err) {
      console.error('Error deleting material:', err)
      alert('자료 삭제 중 오류가 발생했습니다.')
    }
  }

  async function removeQA(item) {
    if (!isAdmin.value || !item.row_key) return

    if (!confirm('정말로 이 질문과 답변을 삭제하시겠습니까?')) return

    try {
      await api.deleteQA({
        week_range: weekRange.value,
        target_audience: targetAudience.value,
        row_key: item.row_key
      })
      await loadQAList()
      alert('항목이 삭제되었습니다.')
    } catch (err) {
      console.error('Error deleting QA:', err)
      alert('항목 삭제 중 오류가 발생했습니다.')
    }
  }

  function clearError() {
    error.value = null
  }

  function setMenu(menu) {
    currentMenu.value = menu
    error.value = null
  }

  return {
    // 상태
    weeks,
    currentWeekIndex,
    selectedWeekIndex,
    targetAudience,
    targetAudiences,
    lessonData,
    generatedMaterial,
    isGenerating,
    isCachedMaterial,
    presentationHtml,
    isPresentationGenerating,
    qaList,
    chatHistory,
    isChatLoading,
    isLoading,
    error,
    isAdmin,
    currentMenu,

    // Getters
    selectedWeek,
    weekRange,
    isAdminPath,

    // Actions
    loadInitialData,
    loadLessonData,
    selectWeek,
    setTargetAudience,
    generateMaterial,
    sendChatMessage,
    loadQAList,
    loginAsAdmin,
    logoutAdmin,
    removeMaterial,
    removeQA,
    setMenu,
    clearError
  }
})
