export default [
  {
    ignores: ['dist', 'node_modules', 'build', '*.test.js', '*.spec.js']
  },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
    rules: {
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }],
      'no-console': 'warn',
      'no-debugger': 'error',
      'semi': ['error', 'always'],
      'quotes': ['error', 'single']
    },
  },
];