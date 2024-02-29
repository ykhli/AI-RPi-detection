import { FilesResponse } from '@/app/api/files/route'
import { headers } from 'next/headers'
import styles from './page.module.css'

export default async function Page () {
  const host = headers().get('host')
  const res = await fetch(`http://${host}/api/files/`, {
    method: 'GET',
    cache: 'no-store'
  })
  const files: FilesResponse = await res.json()
  console.log(files)
  return (
    <body className={styles.body}>
    <div className={styles.list}>
      <h2>Available videos</h2>
      <ul>
        {files.map((f, index) => (
          <li key={f.key}><span>{index + 1}. {f.displayName}</span></li>
        ))}
      </ul>
    </div>
    </body>
  )
}
