const config = require('@lobehub/lint').eslint;

config.extends.push('plugin:@next/next/recommended');

config.rules['unicorn/no-negated-condition'] = 0;
config.rules['unicorn/prefer-type-error'] = 0;
config.rules['unicorn/prefer-logical-operator-over-ternary'] = 0;
config.rules['unicorn/no-null'] = 0;
config.rules['unicorn/no-typeof-undefined'] = 0;
config.rules['unicorn/explicit-length-check'] = 0;
config.rules['unicorn/prefer-code-point'] = 0;
config.rules['no-extra-boolean-cast'] = 0;
config.rules['unicorn/no-useless-undefined'] = 0;
config.rules['react/no-unknown-property'] = 0;
config.rules['unicorn/prefer-ternary'] = 0;
config.rules['unicorn/prefer-spread'] = 0;
config.rules['unicorn/catch-error-name'] = 0;
config.rules['unicorn/no-array-for-each'] = 0;
config.rules['unicorn/prefer-number-properties'] = 0;
config.rules['@typescript-eslint/no-unused-vars'] = [
  'warn',
  {
    vars: 'all',
    varsIgnorePattern: '^_',
    args: 'after-used',
    argsIgnorePattern: '^_',
  },
];

config.rules['unused-imports/no-unused-vars'] = [
  'warn',
  {
    vars: 'all',
    varsIgnorePattern: '^_',
    args: 'after-used',
    argsIgnorePattern: '^_',
  },
];
config.rules['@typescript-eslint/no-empty-interface'] = 'off';
config.rules['unicorn/consistent-function-scoping'] = 'off';
config.rules['@typescript-eslint/ban-types'] = [
  'error',
  {
    types: {
      '{}': false,
    },
    extendDefaults: true,
  },
];
config.rules['react-hooks/rules-of-hooks'] = 'warn';
config.rules['no-async-promise-executor'] = 'warn';
config.rules['unicorn/no-array-callback-reference'] = 'warn'; // 如果是 unicorn 报的
config.rules['guard-for-in'] = 'warn';
config.rules['@typescript-eslint/no-unused-expressions'] = 'warn';
config.rules['sort-keys-fix/sort-keys-fix'] = 'warn';

module.exports = config;
