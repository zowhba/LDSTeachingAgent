/**
 * API 클라이언트
 * FastAPI 백엔드와 통신하는 함수들
 */

import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5분 타임아웃 (AI 생성, 프리젠테이션 생성에 시간이 걸릴 수 있음)
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 사용 가능한 주차 목록 가져오기
 */
export async function getAvailableWeeks() {
  const response = await api.get('/weeks')
  return response.data
}

/**
 * 현재 주차 정보 가져오기
 */
export async function getCurrentWeek() {
  const response = await api.get('/weeks/current')
  return response.data
}

/**
 * 특정 주차의 공과 정보 가져오기
 */
export async function getCurriculumByWeek(weekData) {
  const response = await api.post('/curriculum', weekData)
  return response.data
}

/**
 * 공과 자료 생성
 */
export async function generateMaterial(data) {
  const response = await api.post('/generate-material', data)
  return response.data
}

/**
 * 채팅 응답 생성
 */
export async function sendChatMessage(data) {
  const response = await api.post('/chat', data)
  return response.data
}

/**
 * 캐시된 공과 자료 가져오기
 */
export async function getCachedMaterial(weekRange, targetAudience, lessonTitle) {
  const encodedWeekRange = encodeURIComponent(weekRange)
  const encodedAudience = encodeURIComponent(targetAudience)
  const encodedTitle = encodeURIComponent(lessonTitle)

  const response = await api.get(`/cached-material/${encodedWeekRange}/${encodedAudience}/${encodedTitle}`)
  return response.data
}

/**
 * Q&A 목록 가져오기
 */
export async function getQAList(weekRange, targetAudience) {
  const encodedWeekRange = encodeURIComponent(weekRange)
  const encodedAudience = encodeURIComponent(targetAudience)
  const response = await api.get(`/qa/${encodedWeekRange}/${encodedAudience}`)
  return response.data
}

/**
 * 대상 그룹 목록 가져오기
 */
export async function getTargetAudiences() {
  const response = await api.get('/target-audiences')
  return response.data
}

/**
 * 관리자 로그인
 */
export async function adminLogin(password) {
  const response = await api.post('/admin/login', { password })
  return response.data
}

/**
 * 공과 자료 삭제 (관리자)
 */
export async function deleteMaterial(data) {
  const response = await api.post('/admin/delete-material', data)
  return response.data
}

/**
 * Q&A 삭제 (관리자)
 */
export async function deleteQA(data) {
  const response = await api.post('/admin/delete-qa', data)
  return response.data
}

// === 프리젠테이션 API ===
export async function generatePresentation(data) {
  const response = await api.post('/generate-presentation', data)
  return response.data
}

export async function getCachedPresentation(weekRange, targetAudience, lessonTitle) {
  const encodedWeekRange = encodeURIComponent(weekRange)
  const encodedAudience = encodeURIComponent(targetAudience)
  const encodedTitle = encodeURIComponent(lessonTitle)
  const response = await api.get(`/cached-presentation/${encodedWeekRange}/${encodedAudience}/${encodedTitle}`)
  return response.data
}

// === 게시판 API ===
export async function getBoardPosts() {
  const response = await api.get('/board')
  return response.data
}

export async function createBoardPost(data) {
  const response = await api.post('/board', data)
  return response.data
}

export async function verifyPostPassword(data) {
  const response = await api.post('/board/verify-password', data)
  return response.data
}

export async function updateBoardPost(rowKey, data) {
  const response = await api.put(`/board/${rowKey}`, data)
  return response.data
}

export async function deleteBoardPost(rowKey, password) {
  const response = await api.delete(`/board/${rowKey}`, { params: { password } })
  return response.data
}

export default api
