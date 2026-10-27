<template>
  <n-config-provider
    :theme="darkTheme"
    :theme-overrides="themeOverrides"
    :locale="zhCN"
    :date-locale="dateZhCN"
  >
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider :max="4">
          <router-view />
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import {
  NConfigProvider,
  NDialogProvider,
  NMessageProvider,
  NNotificationProvider,
  darkTheme,
  dateZhCN,
  zhCN,
  type GlobalThemeOverrides,
} from 'naive-ui'

const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#5fd3f3',
    primaryColorHover: '#8be6ff',
    primaryColorPressed: '#3aa8c8',
    primaryColorSuppl: '#4ea8ff',
    infoColor: '#4ea8ff',
    successColor: '#8bffb0',
    warningColor: '#ffcc66',
    errorColor: '#ff5f7e',
    bodyColor: '#050914',
    cardColor: '#0a1730',
    modalColor: '#0a1730',
    popoverColor: '#0a1730',
    tableColor: '#0a1730',
    inputColor: '#040a16',
    borderColor: '#1b3766',
    textColorBase: '#d7e7ff',
    textColor1: '#d7e7ff',
    textColor2: '#8fb3e8',
    textColor3: '#5f7fb3',
    fontFamily: "'Noto Sans SC', 'Microsoft YaHei', 'PingFang SC', system-ui, sans-serif",
    borderRadius: '7px',
    borderRadiusSmall: '5px',
  },
  Button: {
    borderRadiusMedium: '7px',
    borderRadiusSmall: '5px',
    heightMedium: '38px',
    fontWeight: '600',
  },
  Input: {
    borderRadius: '6px',
    border: '2px solid #1b3766',
    borderHover: '2px solid #2f60c4',
    borderFocus: '2px solid #5fd3f3',
    boxShadowFocus: '0 0 0 3px rgba(95, 211, 243, 0.1)',
    color: 'rgba(4, 10, 22, 0.88)',
    colorFocus: 'rgba(6, 15, 32, 0.94)',
  },
  Modal: {
    color: '#0a1730',
    borderRadius: '10px',
  },
  Card: {
    color: '#0a1730',
    borderColor: '#1b3766',
    borderRadius: '10px',
  },
  Dialog: {
    color: '#0a1730',
    borderRadius: '10px',
    titleTextColor: '#d7e7ff',
    textColor: '#8fb3e8',
  },
  Dropdown: {
    color: '#0a1730',
    optionTextColor: '#d7e7ff',
    optionColorHover: 'rgba(58, 110, 216, 0.28)',
    borderRadius: '7px',
  },
  Notification: {
    color: '#0a1730',
    borderRadius: '10px',
  },
  Message: {
    color: '#0a1730',
    textColor: '#d7e7ff',
    borderRadius: '7px',
  },
  Switch: {
    railColorActive: '#3a6ed8',
  },
}
</script>
