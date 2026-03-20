import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import importX from 'eslint-plugin-import-x'
import prettier from 'eslint-config-prettier'
import globals from 'globals'

/**
 * 根级 ESLint flat config
 *
 * 各子项目通过 import 此配置并按需扩展。
 * 直接在根目录运行 `eslint .` 时，此配置也会生效。
 */

/** 所有前端子项目的 src 目录 */
const frontendSrcGlobs = [
  'frontend/src/**/*.{ts,tsx}',
  '素材抓取/content-marketing/frontend/src/**/*.{ts,tsx}',
  'KV生成/frontend/src/**/*.{ts,tsx}',
  '表情包/frontend/src/**/*.{ts,tsx}',
  'shared/frontend/**/*.{ts,tsx}',
]

// ── 基础：可复用的配置块 ──────────────────────────────

/** TypeScript 基础规则 */
export const tsBase = tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
)

/** React Hooks + React Refresh 插件 */
export const reactConfig = [
  {
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    },
  },
]

/** import 排序与规范 */
export const importConfig = [
  {
    plugins: {
      'import-x': importX,
    },
    rules: {
      'import-x/order': [
        'warn',
        {
          groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index', 'type'],
          'newlines-between': 'always',
          alphabetize: { order: 'asc', caseInsensitive: true },
        },
      ],
      'import-x/no-duplicates': 'warn',
    },
  },
]

/** 通用代码质量规则 */
export const qualityRules = [
  {
    rules: {
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'no-debugger': 'warn',
      'no-alert': 'warn',
      'prefer-const': 'error',
      'no-var': 'error',
      eqeqeq: ['error', 'always', { null: 'ignore' }],
      curly: ['error', 'multi-line'],

      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_', caughtErrorsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/consistent-type-imports': [
        'warn',
        { prefer: 'type-imports', fixStyle: 'inline-type-imports' },
      ],
    },
  },
]

// ── 根级完整配置 ──────────────────────────────────────

export default tseslint.config(
  // 全局忽略
  {
    ignores: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/.vite/**',
      '**/coverage/**',
      '**/*.config.{js,ts,mjs,cjs}',
      '**/vite-env.d.ts',
    ],
  },

  // TypeScript 基础
  ...tsBase,

  // 前端项目专用：React + import
  {
    files: frontendSrcGlobs,
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2020,
      },
    },
  },
  ...reactConfig.map((cfg) => ({ ...cfg, files: frontendSrcGlobs })),
  ...importConfig.map((cfg) => ({ ...cfg, files: frontendSrcGlobs })),

  // 通用质量规则
  ...qualityRules,

  // Prettier 兼容（关闭冲突的格式化规则）
  prettier,
)
