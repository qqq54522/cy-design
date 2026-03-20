import tseslint from 'typescript-eslint'
import prettier from 'eslint-config-prettier'
import globals from 'globals'
import { tsBase, reactConfig, importConfig, qualityRules } from '../eslint.config.js'

export default tseslint.config(
  { ignores: ['dist/**', '.vite/**', 'node_modules/**'] },

  ...tsBase,

  {
    files: ['src/**/*.{ts,tsx}'],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2020,
      },
    },
  },

  ...reactConfig.map((cfg) => ({ ...cfg, files: ['src/**/*.{ts,tsx}'] })),
  ...importConfig.map((cfg) => ({ ...cfg, files: ['src/**/*.{ts,tsx}'] })),
  ...qualityRules,

  prettier,
)
