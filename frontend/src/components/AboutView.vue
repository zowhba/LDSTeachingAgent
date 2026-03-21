<template>
  <div class="space-y-6 max-w-4xl mx-auto py-4">
    <div class="card-church p-8">
      <div class="flex items-center mb-8 pb-4 border-b" style="border-color: var(--church-light-gray);">
        <div class="w-12 h-12 rounded-full flex items-center justify-center mr-5" style="background-color: var(--church-navy);">
          <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h2 class="text-2xl font-bold" style="color: var(--church-navy);">소개 및 이용 가이드</h2>
          <p class="text-gray-500">교사분들의 공과 준비를 지원하기 위한 실험적 프로젝트입니다</p>
        </div>
      </div>

      <div class="prose prose-lg max-w-none space-y-8" style="color: var(--church-gray);">
        <section>
          <h3 class="text-xl font-bold flex items-center mb-4" style="color: var(--church-navy);">
            <span class="w-6 h-6 rounded bg-gold-light flex items-center justify-center mr-3 text-sm">01</span>
            공과 준비 도우미란?
          </h3>
          <p class="leading-relaxed">
            이 도구는 <strong>신갈와드 주일학교 회장단</strong>에서 교사분들의 공과 준비를 돕고자 자체적으로 기획·제작한 
            <strong>실험적인 프로젝트</strong>입니다 (교회의 공식 사이트가 아닙니다).
          </p>
          <p class="leading-relaxed mt-3">
            후기성도 예수 그리스도 교회의 공식 커리큘럼(와서 나를 따르라) 내용을 기반으로, 
            AI가 매주 공과의 핵심 메시지를 정리하고 대상(성인, 초등회 등)에 맞춤화된 보조 자료와 토론 질문 등을 자동으로 생성합니다.
            교사분들이 공과를 준비하실 때 아이디어를 얻거나 참고 자료로 활용하실 수 있습니다.
          </p>
        </section>

        <section>
          <h3 class="text-xl font-bold flex items-center mb-4" style="color: var(--church-navy);">
            <span class="w-6 h-6 rounded bg-gold-light flex items-center justify-center mr-3 text-sm">02</span>
            활용 팁
          </h3>
          <ul class="list-disc list-inside space-y-3 pl-4">
            <li><strong>주차 선택:</strong> 상단의 공과 주차 콤보박스에서 원하시는 주차를 선택하시면, 해당 주의 공과 내용이 자동으로 로드됩니다. 캐시된 자료가 없는 경우 AI가 새로 생성을 시작합니다.</li>
            <li><strong>대상 그룹 설정:</strong> 가르치시는 대상(성인, 초등회 등)을 선택하시면, 해당 그룹에 적합한 수준과 방식으로 맞춤 자료가 제공됩니다.</li>
            <li><strong>프레젠테이션 자동 생성:</strong> 텍스트 공과 자료 외에도, 실제 수업시간에 화면에 띄워 바로 가르칠 수 있는 <strong>고품질의 시각적 프레젠테이션(HTML)</strong>이 백그라운드에서 함께 생성됩니다. 상단의 '발표자료 다운로드' 버튼을 눌러 활용해 보세요.</li>
            <li><strong>AI 질문 기능:</strong> 생성된 자료 하단의 채팅창에서 자유롭게 질문하실 수 있습니다. 예를 들어 "이 공과의 토론 질문을 3가지 더 만들어줘" 또는 "이 내용을 10분 수업으로 요약해줘" 같은 요청이 가능합니다.</li>
            <li><strong>이전 질문 확인:</strong> 상단의 '이전 질문 확인' 콤보박스에서 이전에 했던 질문과 답변을 다시 확인하실 수 있습니다.</li>
          </ul>
        </section>

        <section class="bg-blue-50 p-6 rounded-xl border border-blue-100">
          <h3 class="text-lg font-bold mb-3" style="color: var(--church-navy);">참고 사항</h3>
          <p class="text-sm leading-relaxed">
            AI가 생성한 내용은 때로 부정확하거나 교리를 완전하게 담아내지 못할 수도 있습니다. 
            생성된 내용은 공과 준비 시 참고 자료로 활용하시되, 공식 경전 및 교회 자료와 함께 확인해주시면 좋겠습니다.
            본 도구는 교회의 공식 출판물이 아닌, 와드 차원의 자체 지원 프로젝트임을 참고해주시기 바랍니다.
          </p>
        </section>
      </div>

      <!-- 만든 이 소개 -->
      <div class="mt-12 pt-8 border-t text-center" style="border-color: var(--church-light-gray);">
        <h4 class="text-sm font-semibold mb-4 uppercase tracking-widest text-gray-400">제작 및 운영</h4>
        <div class="inline-block p-5 rounded-lg bg-gray-50 border border-gray-100 shadow-sm">
          <p class="text-base font-medium mb-2" style="color: var(--church-navy);">후기성도 예수 그리스도 교회 신갈와드 주일학교 회장단</p>
          <div class="flex flex-wrap justify-center gap-x-4 gap-y-1 text-sm text-gray-500">
            <span>회장: 이재섭 형제</span>
            <span class="w-px h-3 bg-gray-300 self-center hidden sm:block"></span>
            <span>1보좌: 정의철 형제</span>
            <span class="w-px h-3 bg-gray-300 self-center hidden sm:block"></span>
            <span>2보좌: 곽영헌 형제</span>
            <span class="w-px h-3 bg-gray-300 self-center hidden sm:block"></span>
            <span>서기: 오지웅 형제</span>
          </div>
          <div class="mt-3 pt-3 border-t border-gray-200">
            <p class="text-xs text-gray-400">
              개발 담당: 오지웅 형제 · 
              <a href="mailto:zowhba@naver.com" class="text-blue-400 hover:text-blue-600 transition">zowhba@naver.com</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-gold-light {
  background-color: var(--church-gold-light);
  color: var(--church-navy);
}
</style>
