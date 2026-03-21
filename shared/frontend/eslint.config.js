import tseslint from 'typescript-eslint'
import prettier from 'eslint-config-prettier'
import globals from 'globals'
import { tsBase, reactConfig, importConfig, qualityRules } from '../../eslint.config.js'

const sharedSourceGlobs = [
  'index.ts',
  'api/**/*.ts',
  'components/**/*.ts',
  'components/**/*.tsx',
  'hooks/**/*.ts',
  'hooks/**/*.tsx',
  'utils/**/*.ts',
  'types/**/*.ts',
  'constants/**/*.ts',
]

export default tseslint.config(
  { ignores: ['dist/**', '.vite/**', 'node_modules/**'] },

  ...tsBase,

  {
    files: sharedSourceGlobs,
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2020,
      },
    },
  },
  {
    files: ['vite.config.base.ts'],
    languageOptions: {
      globals: {
        ...globals.node,
      },
    },
  },

  ...reactConfig.map((cfg) => ({ ...cfg, files: sharedSourceGlobs })),
  ...importConfig.map((cfg) => ({ ...cfg, files: [...sharedSourceGlobs, 'vite.config.base.ts'] })),
  ...qualityRules,

  prettier,
)
